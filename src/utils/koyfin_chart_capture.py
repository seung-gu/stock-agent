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
from src.config import CHART_OUTPUT_DIR


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
        
        self.driver = webdriver.Firefox(options=options)
        self.driver.maximize_window()
        
        mode = "headless" if self.headless else "visible"
        self._log(f"✅ Firefox initialized ({mode}, maximized)")
    
    def _close_popup(self):
        """Close initial Koyfin popup with ESC key."""
        self._log("Closing popup...")
        time.sleep(5)
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(2)
        self._log("✅ Popup closed")
    
    def _find_visible_input(self) -> Optional[any]:
        """Find first visible input element."""
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        return next((inp for inp in inputs if inp.is_displayed()), None)
    
    def _click_button_by_text(self, text: str, case_sensitive: bool = False) -> bool:
        """
        Click button containing specific text.
        
        Args:
            text: Text to search for in button
            case_sensitive: Whether to match case (default: False)
            
        Returns:
            True if button found and clicked, False otherwise
        """
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            try:
                btn_text = btn.text if case_sensitive else btn.text.lower()
                search_text = text if case_sensitive else text.lower()
                
                if search_text in btn_text and btn.is_displayed():
                    btn.click()
                    return True
            except:
                continue
        return False
    
    def _search_and_select_chart(self, ticker: str):
        """
        Search for ticker and select GF.PE (NTM P/E) chart.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Search box element for reuse
        """
        self._log(f"Searching for '{ticker} GF.PE'...")
        
        # Click search trigger
        search_trigger = self.driver.find_element(
            By.XPATH, 
            "//*[contains(text(), 'Search for a name, ticker, or function')]"
        )
        self.driver.execute_script("arguments[0].click();", search_trigger)
        time.sleep(1)
        
        # Find and use search box
        search_box = self._find_visible_input()
        if not search_box:
            raise Exception("Search box not found")
        
        # Search for ticker
        search_box.send_keys(ticker)
        time.sleep(0.5)
        search_box.send_keys(Keys.RETURN)
        time.sleep(0.3)
        
        # Search for GF.PE chart
        search_box.send_keys(" GF.PE")
        time.sleep(0.5)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)
        
        self._log(f"✅ Selected {ticker} GF.PE chart")
        return search_box
    
    def _add_historical_price(self, search_box):
        """
        Add 'Historical Price' metric to the chart.
        
        Args:
            search_box: Previously found search box element
        """
        self._log("Adding Historical Price metric...")
        time.sleep(1)
        
        # Click 'Add Metric' button
        if not self._click_button_by_text('Add Metric', case_sensitive=True):
            raise Exception("Add Metric button not found")
        
        time.sleep(2)
        
        # Find metric input (different from search box)
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        metric_input = next(
            (inp for i, inp in enumerate(inputs) 
             if inp.is_displayed() and (i > 0 or inp != search_box)),
            None
        )
        
        if not metric_input:
            raise Exception("Metric input not found")
        
        # Type and select Historical Price
        metric_input.send_keys("Historical Price")
        time.sleep(1)
        metric_input.send_keys(Keys.RETURN)
        
        time.sleep(3 if self.headless else 2)
        self._log("✅ Historical Price added")
    
    def _try_direct_10y_button(self) -> bool:
        """Try to click 10Y button directly (for maximized windows)."""
        period_buttons = self.driver.find_elements(
            By.CSS_SELECTOR, 
            ".time-frame-options__item___i_o0Y, .time-frame-option"
        )
        
        for btn in period_buttons:
            try:
                if btn.is_displayed() and btn.text.strip() == '10Y':
                    self.driver.execute_script("arguments[0].click();", btn)
                    self._log("✅ Clicked 10Y (direct button)")
                    return True
            except:
                continue
        return False
    
    def _try_custom_dropdown_10y(self) -> bool:
        """Try to select 10Y from custom dropdown (for smaller windows/headless)."""
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
                    
                    # Find 10Y in dropdown
                    all_elems = self.driver.find_elements(By.XPATH, "//*")
                    for item in all_elems:
                        try:
                            if item.text.strip() == '10Y' and item.is_displayed():
                                self.driver.execute_script("arguments[0].click();", item)
                                self._log("✅ Clicked 10Y (from dropdown)")
                                return True
                        except:
                            continue
                    break
            except:
                continue
        return False
    
    def _set_period_10y(self):
        """Set chart period to 10Y using direct button or custom dropdown."""
        self._log("Setting period to 10Y...")
        
        # Try direct button first, then dropdown
        if not (self._try_direct_10y_button() or self._try_custom_dropdown_10y()):
            self._log("⚠️  10Y not set (button not found)")
        
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
    
    def extract_current_pe(self) -> Optional[float]:
        """
        Extract current Forward P/E (NTM) value from the chart page.
        
        Returns:
            Current Forward P/E value or None if not found
        """
        try:
            page_source = self.driver.page_source
            
            # Pattern: "P/E (NTM)</div><div>35.7x</div>"
            # Look for P/E (NTM) followed by a number with decimal
            pattern = r'P/E \(NTM\)</div><div>([0-9]+\.[0-9]+)x</div>'
            matches = re.findall(pattern, page_source)
            
            if matches:
                # Filter out invalid values and get first valid one
                for match in matches:
                    pe_value = float(match)
                    if pe_value > 1.0:  # P/E should be > 1
                        self._log(f"✅ Extracted Forward P/E (NTM): {pe_value}x")
                        return pe_value
            
            # Fallback: broader pattern
            pattern2 = r'P/E\s*\(NTM\).*?([0-9]+\.[0-9]+)x'
            matches2 = re.findall(pattern2, page_source, re.DOTALL)
            
            if matches2:
                for match in matches2:
                    pe_value = float(match)
                    if pe_value > 1.0:
                        self._log(f"✅ Extracted Forward P/E (NTM): {pe_value}x")
                        return pe_value
            
            self._log("⚠️  Could not extract valid P/E value from page")
            return None
            
        except Exception as e:
            self._log(f"❌ Error extracting P/E: {e}")
            return None
    
    def _save_chart(self, output_path: str) -> bool:
        """
        Save chart image via SHARE dialog.
        
        Args:
            output_path: Destination path
            
        Returns:
            True if successful
        """
        self._log("Saving chart image...")
        
        # Click SHARE button
        if not self._click_button_by_text('share'):
            self._log("⚠️  SHARE button not found")
            return False
        
        time.sleep(2)
        
        try:
            # Find chart image
            chart_img = self._find_chart_image()
            
            if chart_img:
                img_src = chart_img.get_attribute('src')
                if img_src and self._save_image_from_src(img_src, output_path):
                    self._log(f"✅ Chart saved: {output_path}")
                    return True
            
            # Fallback: screenshot
            self._log("⚠️  Chart image not found, using screenshot")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            self.driver.save_screenshot(output_path)
            self._log(f"✅ Screenshot saved: {output_path}")
            return True
            
        except Exception as e:
            self._log(f"⚠️  Error: {e}, using screenshot")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            self.driver.save_screenshot(output_path)
            self._log(f"✅ Screenshot saved: {output_path}")
            return True
    
    def capture(self, ticker: str, output_path: Optional[str] = None) -> tuple[Optional[str], Optional[float]]:
        """
        Capture Koyfin chart for the given ticker and extract current P/E value.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')
            output_path: Optional custom output path.
                        Defaults to 'charts/{ticker}_Koyfin_ForwardPE.png'
        
        Returns:
            Tuple of (chart_path, pe_value) or (None, None) if failed
        """
        if output_path is None:
            output_path = os.path.join(CHART_OUTPUT_DIR, f'{ticker}_Koyfin_ForwardPE.png')
        
        self._log("=" * 80)
        self._log(f"Koyfin Forward P/E Chart: {ticker}")
        self._log("=" * 80)
        
        try:
            self._init_driver()
            
            self._log("Opening Koyfin...")
            self.driver.get(self.KOYFIN_URL)
            
            self._close_popup()
            search_box = self._search_and_select_chart(ticker)
            self._add_historical_price(search_box)
            self._set_period_10y()
            
            # Extract P/E value before saving chart
            pe_value = self.extract_current_pe()
            
            # Save chart
            if self._save_chart(output_path):
                url = self.driver.current_url
                self._log(f"URL: {url}")
                return output_path, pe_value
            
            return None, None
        
        except Exception as e:
            self._log(f"❌ Error for {ticker}: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return None, None
        
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
    
    def capture_multiple(self, tickers: list[str], output_dir: str = 'charts') -> dict[str, Optional[str]]:
        """
        Capture charts for multiple tickers sequentially.
        
        Args:
            tickers: List of ticker symbols
            output_dir: Directory to save charts (default: 'charts')
        
        Returns:
            Dictionary mapping tickers to their output paths (or None if failed)
        """
        results = {}
        for ticker in tickers:
            output_path = f'{output_dir}/{ticker}_Koyfin_ForwardPE.png'
            results[ticker] = self.capture(ticker, output_path)
        
        return results
