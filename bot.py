#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║  Ultimate Skip Bot – Final Edition      ║
║  كل الميزات – مكتمل 100%                ║
║  Anti-Leak | Human | AI | Proxy         ║
║  Telegram | User Journey | Geo Match    ║
║  Monitor | curl_cffi | Web UI           ║
╚══════════════════════════════════════════╝
"""
import asyncio, hashlib, json, logging, os, random, re, time
from collections import deque, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import aiohttp
from aiohttp import web, ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector, ProxyType
from fake_useragent import UserAgent
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import stealth_sync

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    from curl_cffi import requests as curl_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs.txt", encoding="utf-8"), logging.StreamHandler()]
)
logger = logging.getLogger("ApexBot")

CONFIG_FILE = "config.json"
COOKIE_DIR = "data/cookies"
AI_MEMORY_FILE = "data/ai_memory.json"
os.makedirs(COOKIE_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)
fake_ua = UserAgent()

# ----------------------------------------------------------------------
# Device Presets
# ----------------------------------------------------------------------
DEVICE_PRESETS = {
    "windows": {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "viewport": {"width": 1920, "height": 1080}, "mobile": False, "touch": False,
        "locale": "en-US", "tz": "America/New_York"
    },
    "mac": {
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "viewport": {"width": 1680, "height": 1050}, "mobile": False, "touch": False,
        "locale": "en-GB", "tz": "Europe/London"
    },
    "iphone": {
        "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "viewport": {"width": 390, "height": 844}, "mobile": True, "touch": True,
        "locale": "ar-SA", "tz": "Asia/Riyadh"
    },
    "android": {
        "ua": "Mozilla/5.0 (Linux; Android 14; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.113 Mobile Safari/537.36",
        "viewport": {"width": 412, "height": 915}, "mobile": True, "touch": True,
        "locale": "en-US", "tz": "America/Chicago"
    },
    "ipad": {
        "ua": "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "viewport": {"width": 1024, "height": 768}, "mobile": True, "touch": True,
        "locale": "en-US", "tz": "America/Los_Angeles"
    }
}

SOCIAL_REFERRERS = [
    "https://www.facebook.com/", "https://m.facebook.com/", "https://twitter.com/",
    "https://www.instagram.com/", "https://www.linkedin.com/", "https://www.reddit.com/",
    "https://www.tiktok.com/", "https://www.snapchat.com/", "https://www.pinterest.com/",
    "https://t.co/", ""
]

RANDOM_SITES = [
    "https://en.wikipedia.org/wiki/Special:Random",
    "https://www.britannica.com/random",
    "https://news.ycombinator.com/",
    "https://www.reddit.com/r/all/",
    "https://www.producthunt.com/",
    "https://www.quora.com/",
    "https://stackoverflow.com/questions",
    "https://medium.com/",
    "https://www.nytimes.com/",
    "https://www.theguardian.com/international",
]

WEB_USERNAME = os.getenv("WEB_USERNAME", "admin")
WEB_PASSWORD = os.getenv("WEB_PASSWORD", "changeme123")

COUNTRY_LOCALE_MAP = {
    "US": ("en-US", "America/New_York"), "GB": ("en-GB", "Europe/London"),
    "SA": ("ar-SA", "Asia/Riyadh"), "AE": ("ar-AE", "Asia/Dubai"),
    "FR": ("fr-FR", "Europe/Paris"), "DE": ("de-DE", "Europe/Berlin"),
    "EG": ("ar-EG", "Africa/Cairo"), "IN": ("en-IN", "Asia/Kolkata"),
    "BR": ("pt-BR", "America/Sao_Paulo"), "MX": ("es-MX", "America/Mexico_City"),
    "CA": ("en-CA", "America/Toronto"), "AU": ("en-AU", "Australia/Sydney"),
    "JP": ("ja-JP", "Asia/Tokyo"), "KR": ("ko-KR", "Asia/Seoul"),
    "TR": ("tr-TR", "Europe/Istanbul"), "RU": ("ru-RU", "Europe/Moscow"),
    "IT": ("it-IT", "Europe/Rome"), "ES": ("es-ES", "Europe/Madrid"),
}
DEFAULT_LOCALE = "en-US"
DEFAULT_TZ = "America/New_York"

# ----------------------------------------------------------------------
# Stealth Scripts
# ----------------------------------------------------------------------
def generate_advanced_stealth_scripts():
    return f"""
    (() => {{
        const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {{
            const ctx = this.getContext('2d');
            if (ctx) {{
                const shift = {{r: {random.randint(0,5)}, g: {random.randint(0,5)}, b: {random.randint(0,5)}}};
                const imageData = ctx.getImageData(0,0,1,1);
                imageData.data[0] += shift.r; imageData.data[1] += shift.g; imageData.data[2] += shift.b;
                ctx.putImageData(imageData,0,0);
            }}
            return origToDataURL.apply(this, arguments);
        }};
        const getParam = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(p) {{
            if (p === 37445) return 'Intel Inc.';
            if (p === 37446) return 'Intel Iris OpenGL Engine';
            return getParam.call(this, p);
        }};
        const origGetChannel = AudioBuffer.prototype.getChannelData;
        AudioBuffer.prototype.getChannelData = function(ch) {{
            const data = origGetChannel.call(this, ch);
            for (let i=0; i<data.length; i++) data[i] += (Math.random()-0.5)*1e-10;
            return data;
        }};
        Object.defineProperty(navigator, 'plugins', {{get: () => [1, 2, 3]}});
        Object.defineProperty(navigator, 'mimeTypes', {{get: () => [1, 2, 3]}});
        Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
        delete navigator.__proto__.webdriver;
        window.chrome = {{ runtime: {{}} }};
    }})();
    """

# ----------------------------------------------------------------------
# Telegram Notifier
# ----------------------------------------------------------------------
class TelegramNotifier:
    def __init__(self, token="", chat_id=""):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}/sendMessage" if token else ""

    async def send(self, text: str) -> bool:
        if not self.token or not self.chat_id:
            return False
        try:
            payload = {"chat_id": self.chat_id, "text": text[:4096], "parse_mode": "HTML"}
            async with ClientSession(timeout=ClientTimeout(10)) as session:
                async with session.post(self.base_url, json=payload) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.warning(f"Telegram send failed: {e}")
            return False

# ----------------------------------------------------------------------
# ProxyPool
# ----------------------------------------------------------------------
class ProxyPool:
    def __init__(self, max_failures=2, recheck_interval=300, blacklist_duration=3600):
        self._proxies = []
        self._lock = asyncio.Lock()
        self.max_failures = max_failures
        self.recheck_interval = recheck_interval
        self.blacklist_duration = blacklist_duration
        self._blacklist = {}
        self._recheck_task = None

    async def load(self, lines, validate=False):
        proxies = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"): continue
            try:
                p = self._parse(line)
                if p: proxies.append(p)
            except Exception as e:
                logger.warning(f"تخطي بروكسي غير صالح: {line} - {e}")
        async with self._lock:
            self._proxies = proxies
            self._clean_blacklist()
        if validate: await self.validate_all()
        return len(self._proxies)

    def _parse(self, line):
        patterns = [
            r"^(?:(?P<scheme>https?)://)?(?:(?P<user>[^:@]+):(?P<password>[^@]+)@)?(?P<host>[^:]+):(?P<port>\d+)$",
            r"^(?P<host>[^:]+):(?P<port>\d+):(?P<user>[^:]+):(?P<password>.+)$",
        ]
        for pat in patterns:
            m = re.match(pat, line)
            if m:
                g = m.groupdict()
                host = g.get("host")
                port = int(g.get("port", 0))
                scheme = g.get("scheme", "http") or "http"
                user = g.get("user")
                password = g.get("password")
                if not host or not port: continue
                ptype = ProxyType.HTTP if scheme in ("http","https") else ProxyType.SOCKS5
                return {"host": host, "port": port, "username": user, "password": password,
                        "type": ptype, "scheme": scheme, "failures": 0, "enabled": True,
                        "proxy_id": f"{host}:{port}"}
        return None

    def _clean_blacklist(self):
        now = time.time()
        expired = [pid for pid, until in self._blacklist.items() if now > until]
        for pid in expired:
            del self._blacklist[pid]
            for p in self._proxies:
                if p.get("proxy_id") == pid:
                    p["enabled"] = True
                    p["failures"] = 0

    async def get(self):
        async with self._lock:
            self._clean_blacklist()
            active = [p for p in self._proxies if p["enabled"] and p.get("proxy_id") not in self._blacklist]
            return random.choice(active) if active else None

    async def quick_test(self, proxy):
        try:
            conn = ProxyConnector(proxy_type=proxy["type"], host=proxy["host"], port=proxy["port"],
                                  username=proxy.get("username"), password=proxy.get("password"))
            async with ClientSession(connector=conn, timeout=ClientTimeout(6)) as s:
                async with s.get("http://httpbin.org/ip") as r:
                    return r.status == 200
        except: return False

    async def mark_success(self, p):
        async with self._lock:
            p["failures"] = 0
            self._blacklist.pop(p.get("proxy_id"), None)

    async def mark_failure(self, p):
        async with self._lock:
            p["failures"] += 1
            if p["failures"] >= self.max_failures:
                p["enabled"] = False
                self._blacklist[p.get("proxy_id")] = time.time() + self.blacklist_duration
                logger.info(f"تم حظر البروكسي مؤقتاً: {p['host']}:{p['port']}")

    @property
    def active_count(self):
        self._clean_blacklist()
        return sum(1 for p in self._proxies if p["enabled"] and p.get("proxy_id") not in self._blacklist)

    async def validate_all(self, concurrency=30):
        async with self._lock:
            proxies = self._proxies[:]
        sem = asyncio.Semaphore(concurrency)
        async def _test(p):
            async with sem: await self._test_proxy(p)
        await asyncio.gather(*[_test(p) for p in proxies])

    async def _test_proxy(self, proxy):
        try:
            conn = ProxyConnector(proxy_type=proxy["type"], host=proxy["host"], port=proxy["port"],
                                  username=proxy.get("username"), password=proxy.get("password"))
            async with ClientSession(connector=conn, timeout=ClientTimeout(6)) as s:
                async with s.get("http://httpbin.org/ip") as r:
                    proxy["enabled"] = r.status == 200
                    if proxy["enabled"]: proxy["failures"] = 0
        except: proxy["enabled"] = False

# ----------------------------------------------------------------------
# BrowserManager
# ----------------------------------------------------------------------
class BrowserManager:
    def __init__(self, cookie_dir=COOKIE_DIR):
        self.cookie_dir = cookie_dir
        self.playwright = None
        self.browser: Optional[Browser] = None

    async def start(self, dns_server=None, disable_webrtc=True):
        self.playwright = await async_playwright().start()
        args = [
            "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--no-first-run", "--no-default-browser-check",
            "--disable-features=TranslateUI,BlinkGenPropertyTrees,IsolateOrigins,site-per-process",
            "--disable-features=NetworkService,NetworkServiceInProcess",
            "--enable-features=NetworkServiceInProcess",
            "--disable-features=SecureDns",
            "--disable-features=OutOfBlinkCors",
            "--disable-features=BackForwardCache",
            "--disable-features=InterestFeedContentSuggestions",
            "--disable-features=OptimizationHints",
            "--disable-features=MediaRouter",
            "--disable-sync", "--disable-breakpad", "--disable-crash-reporter",
            "--disable-component-update", "--disable-background-networking",
            "--disable-client-side-phishing-detection", "--disable-default-apps",
            "--disable-extensions", "--disable-hang-monitor", "--disable-popup-blocking",
            "--disable-prompt-on-repost", "--disable-web-security",
        ]
        if dns_server:
            args.append(f"--dns-server={dns_server}")
        if disable_webrtc:
            args.append("--force-webrtc-ip-handling-policy=disable_non_proxied_udp")
        self.browser = await self.playwright.chromium.launch(headless=True, args=args)

    async def stop(self):
        if self.browser: await self.browser.close(); self.browser = None
        if self.playwright: await self.playwright.stop(); self.playwright = None

    async def new_context(self, proxy=None, profile_id="", device_name="windows",
                          referrer="", locale=None, timezone=None):
        if not self.browser: raise RuntimeError("المتصفح غير مهيأ")
        device = DEVICE_PRESETS.get(device_name, DEVICE_PRESETS["windows"])
        ua = device["ua"] if random.random() > 0.3 else fake_ua.random
        vp = device["viewport"]
        proxy_cfg = None
        if proxy:
            server = f"{proxy.get('scheme','http')}://{proxy['host']}:{proxy['port']}"
            proxy_cfg = {"server": server}
            if proxy.get("username") and proxy.get("password"):
                proxy_cfg["username"] = proxy["username"]
                proxy_cfg["password"] = proxy["password"]
        loc = locale or device.get("locale", "en-US")
        tz = timezone or device.get("tz", "America/New_York")
        context_options = {
            "viewport": vp, "user_agent": ua,
            "locale": loc, "timezone_id": tz,
            "proxy": proxy_cfg,
            "is_mobile": device["mobile"], "has_touch": device["touch"],
            "permissions": [],
            "geolocation": {"latitude": random.uniform(-90,90), "longitude": random.uniform(-180,180)},
        }
        if referrer:
            context_options["extra_http_headers"] = {"Referer": referrer}
        ctx = await self.browser.new_context(**context_options)
        if profile_id:
            cookie_file = os.path.join(self.cookie_dir, f"{profile_id}.json")
            if os.path.exists(cookie_file):
                try:
                    with open(cookie_file) as f: cookies = json.load(f)
                    await ctx.add_cookies(cookies)
                except: pass
        return ctx

    async def save_cookies(self, ctx, profile_id):
        if not profile_id: return
        try:
            cookies = await ctx.cookies()
            with open(os.path.join(self.cookie_dir, f"{profile_id}.json"), "w") as f:
                json.dump(cookies, f)
        except: pass

    def apply_stealth(self, page: Page):
        stealth_sync(page)
        page.add_init_script(generate_advanced_stealth_scripts())

# ----------------------------------------------------------------------
# AIHandler
# ----------------------------------------------------------------------
class AIHandler:
    def __init__(self, memory_file=AI_MEMORY_FILE, max_age_days=30):
        self.memory_file = memory_file
        self.max_age_days = max_age_days
        self.memory = {}
        self.model = None
        self._enabled = False
        self._save_task = None
        self._dirty = False
        self.load_memory()

    def configure(self, api_key, enabled=True):
        self._enabled = enabled
        if enabled and api_key and HAS_GEMINI:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            if not self._save_task: self._save_task = asyncio.ensure_future(self._periodic_save())
        else:
            self._enabled = False
            if self._save_task: self._save_task.cancel(); self._save_task = None

    @property
    def enabled(self):
        return self._enabled and self.model is not None

    def load_memory(self):
        if not os.path.exists(self.memory_file): return
        try:
            with open(self.memory_file) as f: data = json.load(f)
            cutoff = time.time() - self.max_age_days * 86400
            self.memory = {d: i for d, i in data.items() if isinstance(i, dict) and i.get("timestamp",0) > cutoff}
        except: self.memory = {}

    def save_memory(self, force=False):
        if not force and not self._dirty: return
        try:
            if os.path.exists(self.memory_file): os.replace(self.memory_file, self.memory_file + ".bak")
            with open(self.memory_file, "w") as f: json.dump(self.memory, f, indent=2)
            self._dirty = False
        except: pass

    async def _periodic_save(self, interval=60):
        while True:
            await asyncio.sleep(interval)
            self.save_memory()

    async def get_selectors(self, page: Page):
        domain = urlparse(page.url).netloc
        if domain in self.memory:
            mem = self.memory[domain]
            selectors = mem.get("selectors", [])
            if selectors:
                mem["timestamp"] = time.time()
                mem["hits"] = mem.get("hits",0) + 1
                self._dirty = True
                return selectors
        if not self.enabled: return None
        try:
            body = await page.evaluate("() => document.body.innerText")
            prompt = f"""
            Analyze this link shortener page and return JSON with a list of CSS selectors to click in order.
            Example: {{"selectors": ["#skip_button", ".continue-btn"]}}
            Page text:
            {body[:3000]}
            """
            resp = await asyncio.to_thread(self.model.generate_content, prompt)
            m = re.search(r"\{.*\}", resp.text, re.DOTALL)
            if m:
                data = json.loads(m.group())
                selectors = data.get("selectors", [])
                if selectors:
                    self.memory[domain] = {"selectors": selectors, "timestamp": time.time(), "hits": 1}
                    self._dirty = True
                    return selectors
        except Exception as e: logger.warning(f"AI error: {e}")
        return None

# ----------------------------------------------------------------------
# Geo Helper
# ----------------------------------------------------------------------
async def fetch_country_code(proxy: Optional[Dict[str, Any]]) -> str:
    if not proxy: return ""
    try:
        url = f"http://ip-api.com/json/{proxy['host']}?fields=countryCode"
        async with ClientSession(timeout=ClientTimeout(5)) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("countryCode", "")
    except Exception: pass
    return ""

def get_locale_tz_from_country(country_code: str) -> Tuple[str, str]:
    return COUNTRY_LOCALE_MAP.get(country_code, (DEFAULT_LOCALE, DEFAULT_TZ))

# ----------------------------------------------------------------------
# SkipBot
# ----------------------------------------------------------------------
class SkipBot:
    def __init__(self, proxy_pool, browser, ai):
        self.proxy_pool = proxy_pool
        self.browser = browser
        self.ai = ai
        self.urls = []
        self.workers = 3
        self.delay_base = 1.0
        self.delay_distribution = "triangular"
        self.delay_min = 2.0
        self.delay_max = 12.0
        self.skip_rate = 70
        self.ad_interaction_percent = 30
        self.media_mode = "aggressive"
        self.human_scroll = True
        self.close_popups = True
        self.test_mode = False
        self.proxy_pre_check = False
        self.max_visits_per_hour = 0
        self.use_social_referrer = True
        self.use_random_devices = True
        self.dns_server = "1.1.1.1"
        self.disable_webrtc = True
        self.enable_geo_match = False
        self.schedule = {}
        self.enable_user_journey = False
        self.user_journey_sites = 1
        self.user_journey_use_proxy = False
        self.use_curl_tls = False
        self.telegram_token = ""
        self.telegram_chat_id = ""
        self._tasks = []
        self._stop_event = asyncio.Event()
        self.stats = {"sent":0, "errors":0, "skipped":0, "ad_clicks":0}
        self._lock = asyncio.Lock()
        self.log_queue = deque(maxlen=50)
        self._hourly_counts = defaultdict(int)
        self._hourly_reset = time.time()
        self._semaphore = asyncio.Semaphore(10)
        self.telegram: Optional[TelegramNotifier] = None
        # مراقبة البروكسي
        self._proxy_fail_start = 0.0
        self._proxy_monitor_task: Optional[asyncio.Task] = None
        # مراقبة Gemini
        self._ai_consecutive_fails = 0
        self._max_ai_fails = 3

    def configure(self, cfg):
        for k, v in cfg.items():
            if k == "urls" and isinstance(v, str):
                self.urls = [u.strip() for u in v.splitlines() if u.strip()]
            elif hasattr(self, k):
                setattr(self, k, v)
        if self.telegram_token and self.telegram_chat_id:
            self.telegram = TelegramNotifier(self.telegram_token, self.telegram_chat_id)

    def _get_delay(self):
        if self.delay_distribution == "uniform":
            return random.uniform(self.delay_min, self.delay_max)
        elif self.delay_distribution == "exponential":
            avg = (self.delay_min + self.delay_max) / 2
            lam = 1.0 / avg if avg > 0 else 1.0
            return random.expovariate(lam)
        else:
            return random.triangular(self.delay_min, self.delay_max,
                                     (self.delay_min + self.delay_max) / 2)

    def _reset_hourly_if_needed(self):
        now = time.time()
        if now - self._hourly_reset >= 3600:
            self._hourly_counts.clear()
            self._hourly_reset = now

    def _check_rate_limit(self, url):
        if self.max_visits_per_hour <= 0: return True
        self._reset_hourly_if_needed()
        return self._hourly_counts[url] < self.max_visits_per_hour

    def is_active(self):
        if not self.schedule: return True
        now = datetime.now()
        if "days" in self.schedule and now.weekday() not in self.schedule["days"]:
            return False
        if "hours" in self.schedule:
            h = now.hour
            return any(s <= h < e for s, e in self.schedule["hours"])
        return True

    async def start(self):
        await self.browser.start(dns_server=self.dns_server, disable_webrtc=self.disable_webrtc)
        self._stop_event.clear()
        self._tasks = [asyncio.create_task(self._worker(i)) for i in range(self.workers)]
        self._proxy_fail_start = 0.0
        if not self._proxy_monitor_task:
            self._proxy_monitor_task = asyncio.create_task(self._monitor_proxy())
        if self.telegram:
            await self.telegram.send("🟢 البوت بدأ العمل")

    async def stop(self):
        self._stop_event.set()
        if self._proxy_monitor_task:
            self._proxy_monitor_task.cancel()
            self._proxy_monitor_task = None
        for t in self._tasks: t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        await self.browser.stop()
        if self.telegram:
            await self.telegram.send("🔴 البوت توقف")

    async def _monitor_proxy(self):
        while not self._stop_event.is_set():
            if self.test_mode:
                await asyncio.sleep(10)
                continue
            if self.proxy_pool.active_count == 0:
                if self._proxy_fail_start == 0:
                    self._proxy_fail_start = time.time()
                elif time.time() - self._proxy_fail_start > 120:
                    self._add_log("⛔ لا يوجد بروكسي نشط لمدة دقيقتين – إيقاف تلقائي", "error")
                    if self.telegram:
                        await self.telegram.send("⛔ توقف البوت: لا يوجد بروكسي نشط")
                    await self.stop()
                    return
            else:
                self._proxy_fail_start = 0.0
            await asyncio.sleep(10)

    async def _worker(self, wid):
        await asyncio.sleep(random.uniform(0,3))
        while not self._stop_event.is_set():
            if not self.is_active(): await asyncio.sleep(30); continue
            proxy = None if self.test_mode else await self.proxy_pool.get()
            if not proxy and not self.test_mode:
                await asyncio.sleep(3)
                continue
            if proxy and self.proxy_pre_check:
                if not await self.proxy_pool.quick_test(proxy): continue

            url = None
            attempts = 0
            while url is None and attempts < len(self.urls):
                candidate = random.choice(self.urls)
                if self._check_rate_limit(candidate):
                    url = candidate
                else:
                    attempts += 1
            if url is None: await asyncio.sleep(10); continue

            async with self._semaphore:
                try:
                    await self._process(url, proxy)
                except Exception as e:
                    logger.error(f"Worker {wid}: {e}")
                    self._add_log(f"خطأ: {str(e)[:80]}", "error")
            delay = self._get_delay()
            await asyncio.sleep(delay)

    async def _process(self, url, proxy):
        # إذا استخدمنا curl_cffi مباشرة (اختياري)
        if self.use_curl_tls and HAS_CURL_CFFI:
            if await self._http_visit_curl(url, proxy):
                async with self._lock: self.stats["sent"] += 1
                return

        domain = urlparse(url).netloc
        pid = f"{domain}_{proxy['host']}:{proxy['port']}" if proxy else "direct"
        device_name = random.choice(list(DEVICE_PRESETS.keys())) if self.use_random_devices else "windows"
        referrer = random.choice(SOCIAL_REFERRERS) if self.use_social_referrer else ""

        locale = None
        timezone = None
        if self.enable_geo_match and proxy:
            country = await fetch_country_code(proxy)
            if country:
                locale, timezone = get_locale_tz_from_country(country)
                self._add_log(f"تم التعرف على البلد: {country} -> {locale}/{timezone}", "info")

        # رحلة المستخدم (بدون بروكسي إذا كان user_journey_use_proxy = False)
        if self.enable_user_journey:
            journey_proxy = proxy if self.user_journey_use_proxy else None
            temp_ctx = await self.browser.new_context(
                proxy=journey_proxy, profile_id="", device_name=device_name, referrer=referrer)
            try:
                temp_page = await temp_ctx.new_page()
                self.browser.apply_stealth(temp_page)
                for _ in range(self.user_journey_sites):
                    try:
                        random_site = random.choice(RANDOM_SITES)
                        await temp_page.goto(random_site, wait_until="domcontentloaded", timeout=15000)
                        await self._human_scroll(temp_page)
                        await asyncio.sleep(random.uniform(1,3))
                    except Exception: pass
            finally:
                await temp_ctx.close()

        # السياق الرئيسي للرابط المختصر (بالبروكسي)
        ctx = await self.browser.new_context(proxy, pid, device_name, referrer,
                                             locale=locale, timezone=timezone)
        try:
            page = await ctx.new_page()
            self.browser.apply_stealth(page)

            if self.media_mode == "aggressive":
                await page.route("**/*.{png,jpg,jpeg,gif,svg,mp4,mp3,webm,woff,woff2,avi,mov,ico}", lambda route: route.abort())
            elif self.media_mode == "balanced":
                await page.route("**/*.{mp4,mp3,webm,avi,mov}", lambda route: route.abort())

            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            async with self._lock: self.stats["sent"] += 1
            self._add_log(f"زيارة: {url[:60]}", "info")

            if self.human_scroll:
                await self._human_like_behavior(page)

            if self.close_popups:
                ctx.on("page", lambda p: asyncio.ensure_future(self._close_popup(p)))

            if random.random() * 100 <= self.ad_interaction_percent:
                await self._click_ad(page, ctx)

            if random.random() * 100 <= self.skip_rate:
                selectors = await self._get_selectors_with_monitor(page)
                if selectors:
                    for sel in selectors:
                        try:
                            await asyncio.sleep(random.triangular(1,7,3))
                            await self._human_click(page, sel)
                            await asyncio.sleep(random.uniform(0.8,3))
                        except Exception: pass
                    async with self._lock: self.stats["skipped"] += 1
                    self._add_log("✅ تم التخطي", "success")
                else:
                    self._add_log("⚠️ لم يتم العثور على زر تخطي", "warning")
            else:
                await asyncio.sleep(random.uniform(4,15))
                self._add_log("👤 غادر بدون تخطي", "info")

            await self.browser.save_cookies(ctx, pid)
        except Exception as e:
            logger.error(f"خطأ: {e}")
            self._add_log(f"فشل: {str(e)[:80]}", "error")
        finally:
            await ctx.close()

    async def _http_visit_curl(self, url: str, proxy: Optional[Dict[str, Any]]) -> bool:
        if not HAS_CURL_CFFI: return False
        try:
            proxies = {}
            if proxy:
                scheme = proxy.get("scheme", "http")
                auth = ""
                if proxy.get("username") and proxy.get("password"):
                    auth = f"{proxy['username']}:{proxy['password']}@"
                proxies["http"] = f"{scheme}://{auth}{proxy['host']}:{proxy['port']}"
                proxies["https"] = proxies["http"]
            response = await asyncio.to_thread(
                curl_requests.get, url,
                proxies=proxies,
                impersonate="chrome110",
                timeout=15
            )
            return response.status_code < 400
        except Exception as e:
            logger.warning(f"curl_cffi visit failed: {e}")
            return False

    async def _get_selectors_with_monitor(self, page):
        try:
            selectors = await self.ai.get_selectors(page)
            self._ai_consecutive_fails = 0
            return selectors
        except Exception as e:
            self._ai_consecutive_fails += 1
            logger.warning(f"AI call failed: {e}")
            if self._ai_consecutive_fails >= self._max_ai_fails:
                self._add_log("⚠️ Gemini API فشل 3 مرات – تم تعطيل AI مؤقتاً", "error")
                if self.telegram:
                    await self.telegram.send("⚠️ Gemini API فشل 3 مرات – تم تعطيل AI مؤقتاً")
                self.ai.configure("", enabled=False)
            return None

    async def _human_like_behavior(self, page):
        action = random.choices(
            population=["scroll_only", "scroll_move", "move_click_empty", "idle"],
            weights=[0.3, 0.4, 0.2, 0.1],
            k=1
        )[0]

        if action == "scroll_only":
            await self._human_scroll(page)
            await asyncio.sleep(random.uniform(0.5,2))
        elif action == "scroll_move":
            await self._human_scroll(page)
            await asyncio.sleep(random.uniform(0.2,0.8))
            await self._random_mouse_move(page)
        elif action == "move_click_empty":
            await self._random_mouse_move(page)
            await page.mouse.click(random.randint(200,600), random.randint(200,600))
            await asyncio.sleep(random.uniform(0.3,1.2))
            await self._human_scroll(page)
        elif action == "idle":
            await asyncio.sleep(random.uniform(1,3))
            await self._human_scroll(page)

    async def _human_scroll(self, page):
        await page.evaluate("window.scrollBy(0, 80 + Math.random()*250)")
        await asyncio.sleep(random.uniform(0.6,2.0))
        await page.evaluate("window.scrollBy(0, 150 + Math.random()*400)")
        await asyncio.sleep(random.uniform(0.7,3.0))
        if random.random() < 0.4:
            await page.evaluate("window.scrollBy(0, -120 - Math.random()*200)")
            await asyncio.sleep(random.uniform(0.3,1.0))

    async def _random_mouse_move(self, page):
        x = random.randint(100,700)
        y = random.randint(100,500)
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.1,0.4))

    async def _human_click(self, page, selector):
        element = page.locator(selector).first
        if await element.count() > 0:
            box = await element.bounding_box()
            if box:
                start_x = random.randint(0,800)
                start_y = random.randint(0,600)
                target_x = box["x"] + box["width"]/2 + random.randint(-5,5)
                target_y = box["y"] + box["height"]/2 + random.randint(-5,5)
                steps = random.randint(8,14)
                for i in range(steps):
                    t = (i+1)/steps
                    x = start_x + (target_x - start_x)*t + random.randint(-3,3)
                    y = start_y + (target_y - start_y)*t + random.randint(-3,3)
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.005,0.04))
                await page.mouse.click(target_x, target_y)
            else:
                await element.click(timeout=5000)
        else:
            raise Exception("العنصر غير موجود")

    async def _click_ad(self, page, context):
        try:
            current_host = urlparse(page.url).hostname
            external_links = await page.evaluate(f"""
                () => Array.from(document.querySelectorAll('a[href]'))
                    .map(a => a.href)
                    .filter(href => href.startsWith('http') && !href.includes('{current_host}'))
            """)
            iframes = await page.evaluate("""() => Array.from(document.querySelectorAll('iframe')).map(f => f.src).filter(s => s.startsWith('http'))""")
            candidates = external_links + iframes
            if not candidates:
                ad_elements = await page.evaluate("""() => {
                    const ads = Array.from(document.querySelectorAll('[class*="ad"],[id*="ad"],[class*="banner"],[id*="banner"]'));
                    return ads.length;
                }""")
                if ad_elements > 0:
                    await page.click('[class*="ad"],[id*="ad"],[class*="banner"],[id*="banner"]', timeout=3000)
                    await asyncio.sleep(3)
                    async with self._lock: self.stats["ad_clicks"] += 1
                    self._add_log("🖱️ نقر على إعلان", "success")
                return
            target = random.choice(candidates)
            self._add_log(f"🖱️ محاولة النقر على إعلان: {target[:60]}", "info")
            try:
                async with context.expect_page(timeout=5000) as new_page_info:
                    if target in external_links:
                        await page.click(f'a[href="{target}"]', timeout=3000)
                    else:
                        await page.evaluate(f'window.open("{target}", "_blank")')
                new_page = await new_page_info.value
                await asyncio.sleep(random.uniform(3,6))
                await new_page.close()
                async with self._lock: self.stats["ad_clicks"] += 1
                self._add_log("✅ تم النقر على إعلان وإغلاقه", "success")
            except TimeoutError:
                self._add_log("⚠️ لم يفتح الإعلان نافذة جديدة", "warning")
        except Exception as e:
            self._add_log(f"⚠️ فشل النقر على إعلان: {str(e)[:60]}", "warning")

    async def _close_popup(self, popup):
        try: await popup.close()
        except: pass

    def _add_log(self, msg, level="info"):
        entry = {"time": datetime.now().strftime("%H:%M:%S"), "msg": msg, "level": level}
        self.log_queue.append(entry)
        logger.info(f"{level}: {msg}")
        if level == "error" and self.telegram:
            asyncio.ensure_future(self.telegram.send(f"⚠️ {msg}"))

# ----------------------------------------------------------------------
# WebApp
# ----------------------------------------------------------------------
HTML = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>Apex Skip Bot</title><meta name="viewport" content="width=device-width, initial-scale=1"><script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script><style>*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;padding:20px}.container{max-width:1100px;margin:auto;display:grid;grid-template-columns:1fr 1fr;gap:20px}.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px}.full{grid-column:1/-1}h2{color:#58a6ff;margin-bottom:15px;font-size:1.2em}label{display:block;margin:10px 0 5px;font-size:0.9em}textarea,input,select{width:100%;padding:10px;background:#0d1117;border:1px solid #30363d;border-radius:6px;color:#c9d1d9;font-size:14px;resize:vertical}button{padding:10px 16px;border:none;border-radius:6px;font-weight:bold;cursor:pointer}.btn-start{background:#2ea043;color:white}.btn-stop{background:#da3633;color:white}.btn-action{background:#1f6feb;color:white}.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:15px}.stat-item{background:#0d1117;padding:12px;border-radius:8px;text-align:center}.stat-value{font-size:1.8em;color:#58a6ff;font-weight:bold}.stat-label{color:#8b949e;font-size:0.8em}.log-box{background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:10px;height:200px;overflow-y:auto;font-size:0.85em}.log-entry{padding:2px 0;display:flex;gap:8px}.log-time{color:#58a6ff;font-family:monospace}.log-success{color:#2ea043}.log-error{color:#da3633}.log-warning{color:#d2991d}canvas{margin-top:10px}</style></head><body><div class="container"><div class="card full"><h2>🎛️ لوحة التحكم</h2><div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:15px"><button class="btn-start" id="startBtn" onclick="start()">▶️ تشغيل</button><button class="btn-stop" id="stopBtn" onclick="stop()" disabled>⏹️ إيقاف</button><button class="btn-action" onclick="saveConfig()">💾 حفظ</button></div><div class="stats-grid"><div class="stat-item"><div class="stat-value" id="sent">0</div><div class="stat-label">زيارات</div></div><div class="stat-item"><div class="stat-value" id="skipped">0</div><div class="stat-label">تخطيات</div></div><div class="stat-item"><div class="stat-value" id="adClicks">0</div><div class="stat-label">نقرات إعلانات</div></div><div class="stat-item"><div class="stat-value" id="errors">0</div><div class="stat-label">أخطاء</div></div></div></div><div class="card"><h2>🎯 الروابط والبروكسي</h2><label>الروابط المختصرة</label><textarea id="urls" rows="3"></textarea><label>البروكسيات</label><textarea id="proxies" rows="3" placeholder="ip:port أو host:port:user:pass"></textarea><div style="display:flex;gap:10px;margin-top:10px"><input type="text" id="proxyUrl" placeholder="رابط جلب"><button class="btn-action" onclick="fetchProxies()">جلب</button></div><div style="display:flex;gap:10px;margin-top:10px"><input type="text" id="asocksUrl" placeholder="رابط asocks"><button class="btn-action" onclick="fetchAsocks()">جلب asocks</button></div><label style="margin-top:10px"><input type="checkbox" id="testMode"> وضع الاختبار (بدون بروكسي)</label><label><input type="checkbox" id="proxyPreCheck"> فحص البروكسي قبل الاستخدام</label></div><div class="card"><h2>⚙️ إعدادات التخطي</h2><div style="display:flex;gap:10px"><div style="flex:1"><label>عدد العمال</label><input type="number" id="workers" value="3"></div><div style="flex:1"><label>تأخير أساسي (ث)</label><input type="number" id="delay" value="1" step="0.1"></div></div><div style="display:flex;gap:10px;margin-top:10px"><div style="flex:1"><label>نسبة التخطي %</label><input type="number" id="skipRate" value="70" min="0" max="100"></div><div style="flex:1"><label>أقصى انتظار (ث)</label><input type="number" id="maxWait" value="15" min="5"></div></div><label>مستوى حظر الوسائط</label><select id="mediaMode"><option value="aggressive">عدواني (توفير كبير)</option><option value="balanced">متوازن (حظر الفيديو فقط)</option><option value="full">واقعي (بدون حظر)</option></select><label>أقصى زيارات لكل رابط في الساعة (0 = غير محدود)</label><input type="number" id="maxVisitsPerHour" value="0" min="0"><label>نسبة التفاعل مع الإعلانات %</label><input type="number" id="adInteractionPercent" value="30" min="0" max="100"></div><div class="card"><h2>⏱️ توزيع الفترات الزمنية</h2><label>نوع التوزيع</label><select id="delayDistribution"><option value="triangular">مثلثي (طبيعي)</option><option value="uniform">موحد (عشوائي منتظم)</option><option value="exponential">أسي (محاكاة بشرية)</option></select><div style="display:flex;gap:10px;margin-top:10px"><div style="flex:1"><label>الحد الأدنى للفترة (ث)</label><input type="number" id="delayMin" value="2" step="0.5"></div><div style="flex:1"><label>الحد الأقصى (ث)</label><input type="number" id="delayMax" value="12" step="0.5"></div></div></div><div class="card"><h2>📱 محاكاة الأجهزة ووسائل التواصل</h2><label><input type="checkbox" id="useRandomDevices" checked> استخدام أجهزة عشوائية</label><label><input type="checkbox" id="useSocialReferrer" checked> زيارات من مواقع التواصل</label></div><div class="card"><h2>🌍 مطابقة الموقع الجغرافي</h2><label><input type="checkbox" id="enableGeoMatch"> مطابقة اللغة والمنطقة الزمنية مع بلد البروكسي</label></div><div class="card"><h2>🧭 رحلة المستخدم</h2><label><input type="checkbox" id="enableUserJourney"> محاكاة رحلة المستخدم (زيارة مواقع عشوائية قبل الرابط)</label><label>عدد المواقع العشوائية</label><input type="number" id="userJourneySites" value="1" min="0" max="3"><label><input type="checkbox" id="userJourneyUseProxy"> استخدام البروكسي في رحلة المستخدم (يستهلك بروكسي)</label></div><div class="card"><h2>🔒 بصمة TLS (curl_cffi)</h2><label><input type="checkbox" id="useCurlTls"> استخدام curl_cffi للطلبات المباشرة (يحاكي Chrome)</label><small>يتطلب تثبيت: pip install curl_cffi</small></div><div class="card"><h2>📢 إشعارات تلغرام</h2><label>Bot Token</label><input type="password" id="telegramToken" placeholder="123:abc..."><label>Chat ID</label><input type="text" id="telegramChatId" placeholder="123456789"></div><div class="card"><h2>🧠 Gemini AI</h2><label><input type="checkbox" id="aiEnabled"> تفعيل Gemini</label><label>مفتاح API</label><input type="password" id="geminiKey" placeholder="AIza..."><button class="btn-action" onclick="testGemini()" style="margin-top:5px">اختبار الاتصال</button><div style="margin-top:10px"><span>📚 الذاكرة: <strong id="memoryCount">0</strong> محدد</span><button class="btn-action" onclick="clearMemory()" style="margin-right:5px">مسح</button></div></div><div class="card"><h2>📈 الرسم البياني</h2><canvas id="chart" height="100"></canvas></div><div class="card"><h2>📜 سجل الأحداث</h2><div class="log-box" id="logBox"></div></div></div><script>let chart;const ctx=document.getElementById('chart').getContext('2d');chart=new Chart(ctx,{type:'line',data:{labels:[],datasets:[{data:[],borderColor:'#58a6ff'}]},options:{responsive:true}});let history=[];function updateStats(d){document.getElementById('sent').innerText=d.sent||0;document.getElementById('skipped').innerText=d.skipped||0;document.getElementById('adClicks').innerText=d.ad_clicks||0;document.getElementById('errors').innerText=d.errors||0;if(d.rps!==undefined){history.push(d.rps);if(history.length>20)history.shift();chart.data.labels=history.map((_,i)=>i);chart.data.datasets[0].data=history;chart.update()}if(d.logs){let html='';d.logs.forEach(l=>{let cls=l.level==='success'?'log-success':(l.level==='error'?'log-error':'log-warning');html+=`<div class="log-entry"><span class="log-time">${l.time}</span><span class="${cls}">${l.msg}</span></div>`});document.getElementById('logBox').innerHTML=html;document.getElementById('logBox').scrollTop=document.getElementById('logBox').scrollHeight}}let ws=new WebSocket(`ws://${location.host}/ws`);ws.onmessage=e=>updateStats(JSON.parse(e.data));ws.onclose=()=>setTimeout(()=>location.reload(),2000);function buildConfig(){return{urls:document.getElementById('urls').value,proxies:document.getElementById('proxies').value,workers:parseInt(document.getElementById('workers').value),delay_base:parseFloat(document.getElementById('delay').value),delay_distribution:document.getElementById('delayDistribution').value,delay_min:parseFloat(document.getElementById('delayMin').value),delay_max:parseFloat(document.getElementById('delayMax').value),skip_rate:parseInt(document.getElementById('skipRate').value),max_wait:parseInt(document.getElementById('maxWait').value),media_mode:document.getElementById('mediaMode').value,human_scroll:true,close_popups:true,test_mode:document.getElementById('testMode').checked,proxy_pre_check:document.getElementById('proxyPreCheck').checked,max_visits_per_hour:parseInt(document.getElementById('maxVisitsPerHour').value),ad_interaction_percent:parseInt(document.getElementById('adInteractionPercent').value),use_random_devices:document.getElementById('useRandomDevices').checked,use_social_referrer:document.getElementById('useSocialReferrer').checked,enable_geo_match:document.getElementById('enableGeoMatch').checked,enable_user_journey:document.getElementById('enableUserJourney').checked,user_journey_sites:parseInt(document.getElementById('userJourneySites').value),user_journey_use_proxy:document.getElementById('userJourneyUseProxy').checked,use_curl_tls:document.getElementById('useCurlTls').checked,telegram_token:document.getElementById('telegramToken').value,telegram_chat_id:document.getElementById('telegramChatId').value,ai_enabled:document.getElementById('aiEnabled').checked,gemini_api_key:document.getElementById('geminiKey').value,dns_server:"1.1.1.1",disable_webrtc:true}}async function start(){let cfg=buildConfig();if(!cfg.urls)return alert('أدخل روابط');await fetch('/api/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cfg)});document.getElementById('startBtn').disabled=true;document.getElementById('stopBtn').disabled=false}async function stop(){await fetch('/api/stop',{method:'POST'});document.getElementById('startBtn').disabled=false;document.getElementById('stopBtn').disabled=true}async function saveConfig(){await fetch('/api/config/save',{method:'POST',body:JSON.stringify(buildConfig())});alert('تم الحفظ')}async function fetchProxies(){let url=document.getElementById('proxyUrl').value.trim();if(!url)return alert('أدخل رابط');let r=await fetch('/api/proxies/load',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url})});let d=await r.json();alert(d.proxies?`تم جلب ${d.proxies} بروكسي`:'فشل')}async function fetchAsocks(){let url=document.getElementById('asocksUrl').value.trim();if(!url)return alert('أدخل رابط');let r=await fetch('/api/asocks/fetch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url})});let d=await r.json();alert(d.error?`فشل: ${d.error}`:`تم جلب ${d.proxies} بروكسي`)}async function testGemini(){let key=document.getElementById('geminiKey').value.trim();if(!key)return alert('أدخل مفتاح API');let r=await fetch('/api/gemini/test',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({api_key:key})});let d=await r.json();alert(d.success?'✅ الاتصال ناجح':'❌ فشل')}async function clearMemory(){await fetch('/api/memory/clear',{method:'POST'});document.getElementById('memoryCount').innerText='0'}window.onload=()=>{fetch('/api/status').then(r=>r.json()).then(updateStats);fetch('/api/memory/stats').then(r=>r.json()).then(d=>document.getElementById('memoryCount').innerText=d.count)};</script></body></html>"""

class WebApp:
    def __init__(self, bot: SkipBot, pool: ProxyPool, ai: AIHandler):
        self.bot = bot
        self.pool = pool
        self.ai = ai
        self.app = web.Application(middlewares=[self._auth_middleware])
        self.ws_clients = set()
        self._setup_routes()

    @staticmethod
    async def _auth_middleware(request: web.Request, handler):
        if request.path == "/ws":
            return await handler(request)
        auth = request.headers.get('Authorization')
        if auth:
            try:
                method, credentials = auth.split(' ', 1)
                if method.lower() == 'basic':
                    decoded = aiohttp.helpers.basic_auth_decode(credentials)
                    username, password = decoded
                    if username == WEB_USERNAME and password == WEB_PASSWORD:
                        return await handler(request)
            except: pass
        headers = {'WWW-Authenticate': 'Basic realm="ApexBot"'}
        return web.Response(status=401, headers=headers)

    def _setup_routes(self):
        self.app.router.add_get("/", self.index)
        self.app.router.add_get("/ws", self.ws)
        self.app.router.add_get("/api/status", self.status)
        self.app.router.add_post("/api/start", self.start)
        self.app.router.add_post("/api/stop", self.stop)
        self.app.router.add_post("/api/proxies/load", self.load_proxies)
        self.app.router.add_post("/api/asocks/fetch", self.asocks)
        self.app.router.add_post("/api/gemini/test", self.test_gemini)
        self.app.router.add_get("/api/memory/stats", self.memory_stats)
        self.app.router.add_post("/api/memory/clear", self.clear_memory)
        self.app.router.add_post("/api/config/save", self.save_config)
        self.app.router.add_get("/api/config/load", self.load_config)

    async def index(self, _): return web.Response(text=HTML, content_type="text/html")
    async def ws(self, req):
        ws = web.WebSocketResponse(); await ws.prepare(req); self.ws_clients.add(ws)
        try: async for _ in ws: pass
        finally: self.ws_clients.discard(ws)
        return ws
    async def status(self, _):
        s = self.bot.stats.copy(); s["active_proxies"] = self.pool.active_count; return web.json_response(s)
    async def start(self, req):
        try: cfg = await req.json()
        except: return web.json_response({"error":"بيانات غير صالحة"}, status=400)
        urls = [u.strip() for u in cfg.pop("urls","").splitlines() if u.strip()]
        if not urls: return web.json_response({"error":"الروابط مطلوبة"}, status=400)
        if "proxies" in cfg: await self.pool.load(cfg.pop("proxies").splitlines())
        self.bot.configure(urls=urls, **cfg)
        if cfg.get("ai_enabled") and cfg.get("gemini_api_key"): self.ai.configure(cfg["gemini_api_key"], enabled=True)
        else: self.ai.configure("", enabled=False)
        await self.bot.start()
        return web.json_response({"status":"ok"})
    async def stop(self, _): await self.bot.stop(); return web.json_response({"status":"stopped"})
    async def load_proxies(self, req):
        data = await req.json(); url = data.get("url","")
        if not url: return web.json_response({"error":"رابط فارغ"}, status=400)
        try:
            async with ClientSession(timeout=ClientTimeout(15)) as s:
                async with s.get(url) as r: text = await r.text()
            n = await self.pool.load(text.splitlines())
            return web.json_response({"proxies":n})
        except Exception as e: return web.json_response({"error":str(e)}, status=500)
    async def asocks(self, req):
        data = await req.json(); url = data.get("url","")
        if not url: return web.json_response({"error":"رابط فارغ"}, status=400)
        try:
            async with ClientSession(timeout=ClientTimeout(15)) as s:
                async with s.get(url) as r:
                    if r.status != 200: return web.json_response({"error":f"HTTP {r.status}"}, status=400)
                    text = await r.text()
            try:
                j = json.loads(text)
                if "proxies" in j: lines = j["proxies"]
                elif isinstance(j, list): lines = j
                else: lines = text.splitlines()
            except: lines = text.splitlines()
            n = await self.pool.load(lines)
            return web.json_response({"proxies":n})
        except Exception as e: return web.json_response({"error":str(e)}, status=500)
    async def test_gemini(self, req):
        data = await req.json(); key = data.get("api_key","")
        if not key: return web.json_response({"success":False,"error":"مفتاح فارغ"})
        try:
            if not HAS_GEMINI: return web.json_response({"success":False,"error":"مكتبة Gemini غير مثبتة"})
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content("Say 'Hello'")
            return web.json_response({"success":True,"message":resp.text})
        except Exception as e: return web.json_response({"success":False,"error":str(e)})
    async def memory_stats(self, _): return web.json_response({"count":len(self.ai.memory)})
    async def clear_memory(self, _):
        self.ai.memory = {}; self.ai._dirty = True; self.ai.save_memory(force=True)
        return web.json_response({"status":"cleared"})
    async def save_config(self, req):
        try:
            cfg = await req.json()
            with open(CONFIG_FILE,"w") as f: json.dump(cfg, f, indent=2)
            return web.json_response({"status":"saved"})
        except Exception as e: return web.json_response({"error":str(e)}, status=500)
    async def load_config(self, _):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f: return web.json_response(json.load(f))
        return web.json_response({})
    async def broadcast_loop(self):
        while True:
            await asyncio.sleep(1)
            stats = self.bot.stats.copy(); stats["active_proxies"] = self.pool.active_count; stats["rps"] = 0; stats["logs"] = list(self.bot.log_queue)
            data = json.dumps(stats)
            for ws in list(self.ws_clients):
                try: await ws.send_str(data)
                except: self.ws_clients.discard(ws)
    async def run(self, host="0.0.0.0", port=8080):
        asyncio.create_task(self.broadcast_loop())
        runner = web.AppRunner(self.app); await runner.setup()
        site = web.TCPSite(runner, host, port); await site.start()
        print(f"🚀 واجهة الويب على http://{host}:{port}")
        await asyncio.Event().wait()

async def main():
    pool = ProxyPool()
    browser = BrowserManager()
    ai = AIHandler()
    bot = SkipBot(pool, browser, ai)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f: saved = json.load(f)
            if "proxies" in saved: await pool.load(saved.pop("proxies").splitlines())
            bot.configure(saved)
            if saved.get("ai_enabled") and saved.get("gemini_api_key"): ai.configure(saved["gemini_api_key"], enabled=True)
        except Exception as e: logger.error(f"فشل تحميل الإعدادات: {e}")
    app = WebApp(bot, pool, ai)
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
