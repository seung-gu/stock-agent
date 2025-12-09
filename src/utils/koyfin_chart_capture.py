"""Koyfin chart automation for capturing NTM P/E and Historical Price charts."""

import base64
import re
import time
import os
from typing import Optional

import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.config import CHART_OUTPUT_DIR

try:
    import tkinter as tk
    root = tk.Tk()
    SCREEN_WIDTH = root.winfo_screenwidth()
    SCREEN_HEIGHT = root.winfo_screenheight()
    root.destroy()
except:
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080


class KoyfinChartCapture:
    """
    Automates Koyfin chart capture for NTM P/E ratio with Historical Price overlay.
    
    Features:
    - Supports both headless and visible modes
    - Handles popup dismissal automatically
    - Selects 10Y time period (via direct button or custom dropdown)
    - Saves chart via SHARE dialog to avoid file naming conflicts
    """
    
    KOYFIN_URL = "https://app.koyfin.com/home"
    CHART_SIZE_MIN = (400, 300)  # Minimum size to identify chart image
    
    def __init__(self, headless: bool = False, verbose: bool = True):
        """
        Initialize Koyfin chart capture.
        
        Args:
            headless: Run in headless mode (default: False)
            verbose: Print progress messages (default: True)
        """
        self.headless = headless
        self.verbose = verbose
        self.driver = None
    
    def _log(self, message: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(message)
    
    def _init_driver(self):
        """Initialize Firefox WebDriver with appropriate options."""
        options = FirefoxOptions()
        if self.headless:
            options.add_argument('--headless')
        
        # Disable automation detection
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('useAutomationExtension', False)
        
        # Find Firefox binary path (for snap installations in CI)
        firefox_binary = os.getenv('FIREFOX_BINARY')
        if firefox_binary and os.path.exists(firefox_binary):
            options.binary_location = firefox_binary
            self._log(f"Using Firefox binary from env: {firefox_binary}")
        
        self.driver = webdriver.Firefox(options=options)
        
        # Set window size explicitly (important for SHARE button visibility)
        if self.headless:
            # Headless mode: set explicit size
            self.driver.set_window_size(1920, 1080)
            self._log(f"Window size set to 1920x1080 (headless)")
        else:
            # Visible mode: maximize
            self.driver.maximize_window()
            size = self.driver.get_window_size()
            self._log(f"Window maximized: {size['width']}x{size['height']}")
        
        mode = "headless" if self.headless else "visible"
        self._log(f"✅ Firefox initialized ({mode}, maximized)")
    
    def _close_popup(self):
        """Close initial Koyfin popup with ESC key."""
        self._log("Closing popup...")
        time.sleep(5)
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(2)
        self._log("✅ Popup closed")
    
    def _find_visible_input(self, timeout: int = 10) -> Optional[any]:
        """Find first visible input element with wait."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            return next((inp for inp in inputs if inp.is_displayed()), None)
        except:
            return None
    
    def _click_button_by_text(self, text: str, case_sensitive: bool = False, timeout: int = 10) -> bool:
        """
        Click button containing specific text with wait.
        
        Args:
            text: Text to search for in button
            case_sensitive: Whether to match case (default: False)
            timeout: Maximum wait time in seconds (default: 10)
            
        Returns:
            True if button found and clicked, False otherwise
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            # Wait for at least one button to be present
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "button")))
            
            # Try to find and click the button
            for attempt in range(3):  # Retry up to 3 times
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    try:
                        btn_text = btn.text if case_sensitive else btn.text.lower()
                        search_text = text if case_sensitive else text.lower()
                        
                        if search_text in btn_text and btn.is_displayed():
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                            time.sleep(0.3)
                            btn.click()
                            return True
                    except:
                        continue
                
                if attempt < 2:
                    time.sleep(1)  # Wait before retry
            
            return False
        except:
            return False
    
    def _search_and_select_chart(self, ticker: str):
        """
        Search for ticker and select Historical Price chart first.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Search box element for reuse
        """
        self._log(f"Searching for '{ticker} Historical Price'...")
        
        # Click search trigger with wait
        try:
            wait = WebDriverWait(self.driver, 10)
            search_trigger = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Search for a name, ticker, or function')]"))
            )
            self.driver.execute_script("arguments[0].click();", search_trigger)
            time.sleep(1.5)
        except Exception as e:
            self._log(f"⚠️  Search trigger click failed: {e}")
            raise Exception("Search trigger not found")
        
        # Find and use search box with wait
        search_box = self._find_visible_input(timeout=10)
        if not search_box:
            raise Exception("Search box not found")
        
        # Search for ticker
        search_box.clear()
        search_box.send_keys(ticker)
        time.sleep(1)
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Search for Historical Price Graph
        search_box.send_keys(" Historical Price Graph")
        time.sleep(1.5)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)  # Wait for chart to load
        
        self._log(f"✅ Selected {ticker} Historical Price Graph")
        return search_box
    
    def _add_pe(self, search_box):
        """
        Add 'P/E (NTM P/E)' metric to the chart.
        
        Args:
            search_box: Previously found search box element
        """
        self._log("Adding P/E metric...")
        time.sleep(3)
        
        # Wait for 'Add Metric' button with retry
        self._log("Waiting for 'Add Metric' button...")
        max_retries = 3
        for retry in range(max_retries):
            try:
                # Close dialogs
                try:
                    close_btns = self.driver.find_elements(By.CSS_SELECTOR, ".rc-dialog-close, button[aria-label='Close']")
                    for btn in close_btns:
                        if btn.is_displayed():
                            try:
                                self.driver.execute_script("arguments[0].click();", btn)
                            except:
                                pass
                            time.sleep(0.5)
                except:
                    pass
                
                # Find button (fresh each time)
                wait = WebDriverWait(self.driver, 20)
                add_metric_btn = wait.until(
                    lambda driver: next(
                        (btn for btn in driver.find_elements(By.TAG_NAME, "button")
                         if "Add Metric" in btn.text and btn.is_displayed()),
                        None
                    )
                )
                if not add_metric_btn:
                    raise Exception("Add Metric button not found")
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", add_metric_btn)
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", add_metric_btn)
                self._log("✅ 'Add Metric' button clicked")
                break  # Success
                
            except Exception as e:
                if retry < max_retries - 1:
                    self._log(f"⚠️  Retry {retry + 1}/{max_retries}: {type(e).__name__}")
                    time.sleep(2)
                    continue
                else:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    visible_buttons = [btn.text for btn in buttons if btn.is_displayed() and btn.text]
                    self._log(f"❌ Failed after {max_retries} retries. Buttons: {visible_buttons[:10]}")
                    raise Exception("Add Metric button not found")
        
        time.sleep(3)
        
        # Find metric input (different from search box) with wait
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
        except:
            pass
        
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        metric_input = next(
            (inp for i, inp in enumerate(inputs) 
             if inp.is_displayed() and (i > 0 or inp != search_box)),
            None
        )
        
        if not metric_input:
            raise Exception("Metric input not found")
        
        # Type and select PE
        metric_input.clear()
        metric_input.send_keys("P/E")
        time.sleep(2)
        metric_input.send_keys(Keys.RETURN)
        time.sleep(3)
        
        # Select NTM option (Arrow Down + Return)
        self._log("Selecting NTM option...")
        metric_input.send_keys(Keys.ARROW_DOWN)
        time.sleep(1)
        metric_input.send_keys(Keys.RETURN)
        
        time.sleep(5)
        self._log("✅ P/E (NTM) added")
    
    def _add_peg(self, search_box):
        """
        Add 'PEG (NTM)' metric to the chart.
        
        Args:
            search_box: Previously found search box element
        """
        self._log("Adding PEG metric...")
        time.sleep(3)
        
        # Wait for 'Add Metric' button with retry
        self._log("Waiting for 'Add Metric' button...")
        max_retries = 3
        for retry in range(max_retries):
            try:
                # Close dialogs
                try:
                    close_btns = self.driver.find_elements(By.CSS_SELECTOR, ".rc-dialog-close, button[aria-label='Close']")
                    for btn in close_btns:
                        if btn.is_displayed():
                            try:
                                self.driver.execute_script("arguments[0].click();", btn)
                            except:
                                pass
                            time.sleep(0.5)
                except:
                    pass
                
                # Find button (fresh each time)
                wait = WebDriverWait(self.driver, 20)
                add_metric_btn = wait.until(
                    lambda driver: next(
                        (btn for btn in driver.find_elements(By.TAG_NAME, "button")
                         if "Add Metric" in btn.text and btn.is_displayed()),
                        None
                    )
                )
                if not add_metric_btn:
                    raise Exception("Add Metric button not found")
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", add_metric_btn)
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", add_metric_btn)
                self._log("✅ 'Add Metric' button clicked")
                break  # Success
                
            except Exception as e:
                if retry < max_retries - 1:
                    self._log(f"⚠️  Retry {retry + 1}/{max_retries}: {type(e).__name__}")
                    time.sleep(2)
                    continue
                else:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    visible_buttons = [btn.text for btn in buttons if btn.is_displayed() and btn.text]
                    self._log(f"❌ Failed after {max_retries} retries. Buttons: {visible_buttons[:10]}")
                    raise Exception("Add Metric button not found")
        
        time.sleep(3)
        
        # Find metric input with wait
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
        except:
            pass
        
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        metric_input = next((inp for i, inp in enumerate(inputs) 
                           if inp.is_displayed() and (i > 0 or inp != search_box)), None)
        
        if not metric_input:
            raise Exception("Metric input not found")
        
        # Type and select PEG (NTM will be auto-selected)
        metric_input.clear()
        metric_input.send_keys("PEG")
        time.sleep(2)
        metric_input.send_keys(Keys.RETURN)
        
        time.sleep(5)
        self._log("✅ PEG (NTM) added")
    
    def _click_indicator_settings(self, indicator_name: str = "P/E (NTM)"):
        """Enable Statistical Bands for indicator."""
        self._log(f"Configuring {indicator_name} settings...")
        try:
            # Find element containing indicator name
            indicator_elem = next((e for e in self.driver.find_elements(By.XPATH, f'//*[contains(text(), "{indicator_name}")]')
                                  if e.is_displayed() and indicator_name in e.text), None)
            
            if not indicator_elem:
                return False
            
            # Find cog icon in same container
            parent = indicator_elem
            for _ in range(3):
                parent = parent.find_element(By.XPATH, '..')
                cog = next((c for c in parent.find_elements(By.CSS_SELECTOR, 'i.fa-cog') if c.is_displayed()), None)
                if cog:
                    settings_btn = cog.find_element(By.XPATH, '..')
                    settings_btn.click()
                    time.sleep(2)
                    break
            else:
                return False
            
            # Click Statistical Bands dropdown
            stat_elem = next((e for e in self.driver.find_elements(By.XPATH, '//*[contains(text(), "Statistical Bands")]') 
                             if e.is_displayed()), None)
            if stat_elem:
                parent = stat_elem.find_element(By.XPATH, '..')
                btn = next((b for b in parent.find_elements(By.TAG_NAME, 'button') if b.is_displayed()), None)
                if btn:
                    btn.click()
                    time.sleep(1)
            
            # Enable +1/-1 Standard Deviations
            for dev in ['+1 Standard Deviations', '-1 Standard Deviations']:
                elem = next((e for e in self.driver.find_elements(By.XPATH, f'//*[contains(text(), "{dev}")]') 
                           if e.is_displayed()), None)
                if elem:
                    elem.click()
                    time.sleep(0.5)
            
            # Click "Area" button in Chart Type section
            area_btn = next((b for b in self.driver.find_elements(By.XPATH, '//button[@title="Area"]') 
                           if b.is_displayed()), None)
            if area_btn:
                area_btn.click()
                self._log("✅ Set chart type to Area")
                time.sleep(1)
            
            # Close dialog by clicking settings icon again
            settings_btn.click()
            time.sleep(1)
            
            self._log("✅ Statistical Bands configured")
            return True
        except Exception as e:
            self._log(f"⚠️  Error: {e}")
            return False
    
    def _try_direct_period_button(self, period: str) -> bool:
        """Try to click period button directly (for maximized windows)."""
        period_buttons = self.driver.find_elements(
            By.CSS_SELECTOR, 
            ".time-frame-options__item___i_o0Y, .time-frame-option"
        )
        
        for btn in period_buttons:
            try:
                if btn.is_displayed() and btn.text.strip() == period:
                    self.driver.execute_script("arguments[0].click();", btn)
                    self._log(f"✅ Clicked {period} (direct button)")
                    return True
            except:
                continue
        return False
    
    def _try_custom_dropdown_period(self, period: str) -> bool:
        """Try to select period from custom dropdown (for smaller windows/headless)."""
        # Find and click custom dropdown
        custom_elems = self.driver.find_elements(
            By.XPATH,
            "//*[contains(@class, 'custom') or normalize-space(text())='custom']"
        )
        
        for elem in custom_elems:
            try:
                if elem.is_displayed():
                    self.driver.execute_script("arguments[0].click();", elem)
                    time.sleep(2)
                    
                    # Find period in dropdown
                    all_elems = self.driver.find_elements(By.XPATH, "//*")
                    for item in all_elems:
                        try:
                            if item.text.strip() == period and item.is_displayed():
                                self.driver.execute_script("arguments[0].click();", item)
                                self._log(f"✅ Clicked {period} (from dropdown)")
                                return True
                        except:
                            continue
                    break
            except:
                continue
        return False
    
    def _set_period(self, period: str):
        """
        Set chart period using direct button or custom dropdown.
        
        Args:
            period: Period string (e.g., '1Y', '3Y', '5Y', '10Y', '20Y')
        """
        self._log(f"Setting period to {period}...")
        
        # Try direct button first, then dropdown
        if not (self._try_direct_period_button(period) or self._try_custom_dropdown_period(period)):
            self._log(f"⚠️  {period} not set (button not found)")
        
        time.sleep(1)
    
    def _find_chart_image(self):
        """Find chart image in SHARE dialog."""
        images = self.driver.find_elements(By.TAG_NAME, "img")
        
        for img in images:
            try:
                if img.is_displayed():
                    size = img.size
                    if (size['width'] > self.CHART_SIZE_MIN[0] and 
                        size['height'] > self.CHART_SIZE_MIN[1]):
                        return img
            except:
                continue
        return None
    
    def _save_image_from_src(self, img_src: str, output_path: str) -> bool:
        """
        Save image from src attribute (data URL or regular URL).
        
        Args:
            img_src: Image src attribute
            output_path: Destination path
            
        Returns:
            True if successful, False otherwise
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if img_src.startswith('data:image'):
            # Data URL - extract base64 and save
            match = re.match(r'data:image/(\w+);base64,(.+)', img_src)
            if match:
                image_data = base64.b64decode(match.group(2))
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                return True
        else:
            # Regular URL - download with requests
            response = requests.get(img_src)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
        
        return False
    
    def extract_metrics(self, metric_name: str) -> dict:
        """Extract metrics for a given indicator."""
        metrics = {'value': None, 'plus1_std': None, 'minus1_std': None}
        
        try:
            page_source = self.driver.page_source
            metric_escaped = re.escape(metric_name)
            
            # Extract main value (x suffix is optional)
            value_pattern = rf'{metric_escaped}</div><div>([0-9]+\.[0-9]+)x?</div>'
            matches = re.findall(value_pattern, page_source)
            if matches:
                metrics['value'] = float(matches[0])
                self._log(f"✅ {metric_name}: {metrics['value']}")
            
            # Extract Std Dev values
            for dev, key in [(r'\+1', 'plus1_std'), ('-1', 'minus1_std')]:
                std_pattern = rf'{dev} Std Dev \({metric_escaped}\)</div><div>([0-9]+\.[0-9]+)x?</div>'
                matches = re.findall(std_pattern, page_source)
                if matches:
                    metrics[key] = float(matches[0])
                    self._log(f"✅ {metric_name} {key.replace('_', ' ').title()}: {metrics[key]}")
            
            return metrics
        except Exception as e:
            self._log(f"❌ Error extracting {metric_name} metrics: {e}")
            return metrics
    
    def _save_chart(self, output_path: str) -> bool:
        """
        Save chart image via SHARE dialog.
        
        Args:
            output_path: Destination path
            
        Returns:
            True if successful
        """
        self._log("Saving chart image...")
        
        # Ensure window is large enough for SHARE button to be visible
        current_size = self.driver.get_window_size()
        self._log(f"Current window size: {current_size['width']}x{current_size['height']}")
        if current_size['width'] < 1200 or current_size['height'] < 800:
            self._log("⚠️  Window too small, resizing to 1920x1080")
            self.driver.set_window_size(1920, 1080)
            time.sleep(1)
        
        # Wait for page to fully load
        time.sleep(3)
        
        # Click SHARE button with enhanced search
        self._log("Looking for SHARE button...")
        try:
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "button")))
            
            # Log all visible buttons for debugging
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            visible_button_texts = [btn.text.strip() for btn in all_buttons if btn.is_displayed() and btn.text.strip()]
            self._log(f"Visible buttons: {visible_button_texts[:15]}")
            
            # Try multiple strategies to find SHARE button
            share_btn = None
            
            # Strategy 1: Find by text (case-insensitive)
            for btn in all_buttons:
                if btn.is_displayed() and btn.text.strip().lower() == 'share':
                    share_btn = btn
                    self._log("Found SHARE button (strategy 1: exact text match)")
                    break
            
            # Strategy 2: Find by partial text
            if not share_btn:
                for btn in all_buttons:
                    if btn.is_displayed() and 'share' in btn.text.strip().lower():
                        share_btn = btn
                        self._log(f"Found SHARE button (strategy 2: partial match, text='{btn.text.strip()}')")
                        break
            
            # Strategy 3: Find by aria-label or title
            if not share_btn:
                for btn in all_buttons:
                    if btn.is_displayed():
                        aria_label = btn.get_attribute('aria-label') or ''
                        title = btn.get_attribute('title') or ''
                        if 'share' in aria_label.lower() or 'share' in title.lower():
                            share_btn = btn
                            self._log(f"Found SHARE button (strategy 3: aria-label/title)")
                            break
            
            if not share_btn:
                self._log("❌ SHARE button not found with any strategy")
                return False
            
            # Click the button
            self.driver.execute_script("arguments[0].scrollIntoView(true);", share_btn)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", share_btn)
            self._log("✅ SHARE button clicked")
            time.sleep(3)
            
        except Exception as e:
            self._log(f"❌ Error finding SHARE button: {e}")
            return False
        
        # Click DOWNLOAD button
        self._log("Looking for DOWNLOAD button...")
        try:
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "button")))
            
            # Log all visible buttons after SHARE click
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            visible_button_texts = [btn.text.strip() for btn in all_buttons if btn.is_displayed() and btn.text.strip()]
            self._log(f"Visible buttons after SHARE: {visible_button_texts[:15]}")
            
            download_btn = None
            for btn in all_buttons:
                if btn.is_displayed() and 'download' in btn.text.strip().lower():
                    download_btn = btn
                    break
            
            if not download_btn:
                self._log("❌ DOWNLOAD button not found")
                return False
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", download_btn)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", download_btn)
            self._log("✅ DOWNLOAD button clicked")
            time.sleep(3)
            
        except Exception as e:
            self._log(f"❌ Error finding DOWNLOAD button: {e}")
            return False
        
        # Get chart image
        try:
            self._log("Looking for chart image...")
            chart_img = self._find_chart_image()
            
            if chart_img:
                self._log(f"✅ Chart image found: size={chart_img.size}")
                img_src = chart_img.get_attribute('src')
                self._log(f"Image src type: {img_src[:50] if img_src else 'None'}...")
                
                if img_src and self._save_image_from_src(img_src, output_path):
                    self._log(f"✅ Chart saved: {output_path}")
                    return True
                else:
                    self._log(f"❌ Failed to save image from src")
            else:
                self._log("❌ Chart image not found")
            
            # Fallback: screenshot
            self._log("⚠️  Using screenshot fallback")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            self.driver.save_screenshot(output_path)
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            self._log(f"✅ Screenshot saved: {output_path} ({file_size} bytes)")
            return True
        except Exception as e:
            import traceback
            self._log(f"❌ Exception in _save_chart: {type(e).__name__}: {e}")
            self._log(f"Traceback:\n{traceback.format_exc()}")
            return False
    
    def capture(
        self, 
        ticker: str, 
        output_path: Optional[str] = None,
        period: str = '10Y'
    ) -> tuple[Optional[str], Optional[dict]]:
        """
        Capture Koyfin chart for the given ticker and extract current P/E and PEG values.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')
            output_path: Optional custom output path.
                        Defaults to 'charts/{ticker}_Koyfin_PE_PEG.png'
            period: Chart period ('1Y', '3Y', '5Y', '10Y', '20Y'). Default: '10Y'
        
        Returns:
            Tuple of (chart_path, metrics_dict) or (None, None) if failed
        """
        if output_path is None:
            output_path = os.path.join(CHART_OUTPUT_DIR, f'{ticker}_Koyfin_PE_PEG.png')
        
        self._log("=" * 80)
        self._log(f"Koyfin P/E & PEG Chart: {ticker}")
        self._log("=" * 80)
        
        try:
            self._init_driver()
            
            self._log("Opening Koyfin...")
            self.driver.get(self.KOYFIN_URL)
            
            self._close_popup()
            search_box = self._search_and_select_chart(ticker)
            self._set_period(period)
            
            # Add P/E (NTM)
            pe_metric_name = "P/E (NTM)"
            self._add_pe(search_box)
            self._click_indicator_settings(pe_metric_name)
            
            # Add PEG (NTM)
            peg_metric_name = "PEG (NTM)"
            self._add_peg(search_box)
            self._click_indicator_settings(peg_metric_name)

            # Extract metrics as dict
            pe_data = self.extract_metrics(pe_metric_name)
            peg_data = self.extract_metrics(peg_metric_name)
            
            metrics = {'pe': pe_data, 'peg': peg_data}
            
            # Save chart
            self._log("Attempting to save chart...")
            save_result = self._save_chart(output_path)
            self._log(f"Save chart result: {save_result}")
            
            if save_result:
                url = self.driver.current_url
                self._log(f"URL: {url}")
                self._log(f"✅ SUCCESS: Returning chart_path={output_path}, metrics={metrics}")
                return output_path, metrics
            else:
                self._log(f"❌ FAILED: _save_chart returned False")
                return None, None
        
        except Exception as e:
            self._log(f"❌ EXCEPTION for {ticker}: {type(e).__name__}: {e}")
            import traceback
            self._log(f"Traceback:\n{traceback.format_exc()}")
            return None, None
        
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
    