from pathlib import Path
from playwright.sync_api import sync_playwright
html=(Path(__file__).parent/'index.html').read_text()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'],headless=True)
 page=b.new_page(viewport={'width':1280,'height':900},device_scale_factor=1,accept_downloads=True); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html)
 print('title',page.title(),'stats',page.locator('#stats-output .metric').count());assert page.locator('#stats-output .metric').count()==4
 page.select_option('#subject','영어');assert page.locator('.matrix').count()==1;assert page.locator('#form-compare tr').count()==4;page.select_option('#year','2018');assert '45' in page.locator('#stats-output').inner_text();page.select_option('#year','all')
 page.locator('[data-tab=strategy]').click();assert '검증' in page.locator('#strategy-output').inner_text();page.select_option('#blanks','3');assert '3개 빈칸' in page.locator('#strategy-output').inner_text()
 page.locator('[data-tab=practice]').click();page.locator('.choice').first.click();assert '1 / 45' in page.locator('#practice-count').inner_text();page.locator('#fill').click();assert '45 / 45' in page.locator('#practice-count').inner_text();page.locator('#reveal').click();assert '실제 정답' in page.locator('#practice-result').inner_text();page.locator('#clear').click();assert '0 / 45' in page.locator('#practice-count').inner_text()
 page.locator('[data-tab=data]').click()
 with page.expect_download() as dl:page.locator('#download-csv').click()
 print('download',dl.value.suggested_filename)
 phone=b.new_page(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True);phone.on('pageerror',lambda e:errors.append(str(e)));phone.set_content(html);print('mobile width',phone.evaluate('({inner:innerWidth,doc:document.documentElement.scrollWidth})'));phone.locator('[data-tab=strategy]').click();assert phone.locator('#strategy-output').is_visible();print('errors',errors);assert not errors;b.close()
