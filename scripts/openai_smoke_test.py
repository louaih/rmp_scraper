#!/usr/bin/env python
"""
OpenAI smoke test and diagnostics

This script attempts a minimal call to the OpenAI Responses API and prints
diagnostic information if anything goes wrong (common culprit: mismatched
httpx / openai versions leading to unexpected keyword arguments like 'proxies').

Usage:
  # from project root with virtualenv activated
  python scripts/openai_smoke_test.py

The script reads OPENAI_API_KEY from the environment or a .env file.
"""

import os
import sys
import traceback
import platform
from dotenv import load_dotenv


def print_header(title):
    print('\n' + '=' * 10 + f' {title} ' + '=' * 10)


def safe_get_version(module_name):
    try:
        mod = __import__(module_name)
        return getattr(mod, '__version__', None) or getattr(mod, 'VERSION', None)
    except Exception:
        return None


def main():
    load_dotenv()

    print_header('Environment')
    print('Python:', platform.python_version())
    print('Platform:', platform.platform())

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print('WARNING: OPENAI_API_KEY not found in environment. Set it or create a .env file.')

    # Print installed package versions where possible
    print_header('Installed package versions (best-effort)')
    for pkg in ('openai', 'httpx', 'requests'):
        v = safe_get_version(pkg)
        print(f'{pkg}:', v or 'not installed or version unknown')

    # Import OpenAI and attempt client creation
    try:
        from openai import OpenAI
        import openai as _openai
        openai_ver = getattr(_openai, '__version__', None)
        print('\nImported openai package, version:', openai_ver)
    except Exception as e:
        print('\nERROR: Failed to import the openai package')
        traceback.print_exc()
        print('\nSuggestion: install or upgrade the package:')
        print('  pip install --upgrade openai httpx')
        sys.exit(2)

    try:
        print('\nCreating OpenAI client...')
        # Try to create a client using the explicit api_key if available
        client = OpenAI(api_key=api_key) if api_key else OpenAI()
        print('Client created successfully')
    except TypeError as e:
        print('\nTYPE ERROR during client initialization:')
        print(str(e))
        # Common symptom: underlying HTTP client (e.g., httpx) does not accept
        # a `proxies` kwarg passed by the OpenAI client. Check httpx version.
        try:
            import httpx
            print('httpx version detected:', getattr(httpx, '__version__', None))
        except Exception:
            print('httpx not importable')

        print('\nSuggested fixes:')
        print('  1) Upgrade httpx and openai to recent versions:')
        print('       pip install --upgrade httpx openai')
        print('  2) If using a pinned requirements.txt, update it to include httpx>=0.24.0')
        print('  3) Recreate your virtualenv and reinstall dependencies if issues persist')
        sys.exit(3)
    except Exception as e:
        print('\nUnexpected error creating OpenAI client:')
        traceback.print_exc()
        sys.exit(4)

    # Attempt a minimal Responses API call
    try:
        print_header('Making a small API call (Responses.create)')
        resp = client.responses.create(model='gpt-3.5-turbo', input='Hello from smoke test', max_output_tokens=40)

        # Try helpful extraction patterns
        text = None
        if hasattr(resp, 'output_text') and resp.output_text:
            text = resp.output_text
        elif getattr(resp, 'output', None):
            try:
                for item in resp.output:
                    if getattr(item, 'content', None):
                        for c in item.content:
                            if isinstance(c, str):
                                text = c
                                break
                            if isinstance(c, dict) and c.get('text'):
                                text = c.get('text')
                                break
                    if text:
                        break
            except Exception:
                pass
        elif getattr(resp, 'choices', None):
            try:
                ch = resp.choices[0]
                if getattr(ch, 'message', None):
                    text = ch.message.get('content') or ch.message.get('text')
                elif getattr(ch, 'text', None):
                    text = ch.text
            except Exception:
                pass

        print('\nAPI call succeeded. Extracted text:')
        print(text or repr(resp))
        print('\nSmoke test PASSED')
        return 0

    except Exception as e:
        print('\nAPI call failed with exception:')
        traceback.print_exc()

        msg = str(e).lower()
        if 'insufficient_quota' in msg or 'quota' in msg:
            print('\nDiagnosis: API key exists but account has insufficient quota or no access to the requested model.')
            print('Check billing and model access in your OpenAI account.')
            return 5
        if 'rate_limit' in msg or '429' in msg:
            print('\nDiagnosis: Rate limit (429). Retry after a short wait or reduce request rate.')
            return 6
        if 'proxies' in msg or 'unexpected keyword' in msg or 'unexpected keyword argument' in msg:
            print('\nDiagnosis: Underlying HTTP client does not accept a kwarg OpenAI is providing (commonly proxies).')
            try:
                import httpx
                print('httpx version:', getattr(httpx, '__version__', None))
            except Exception:
                print('httpx not installed or not importable')
            print('Suggested fix: pip install --upgrade httpx openai')
            return 7

        print('\nIf the error is unexpected, try upgrading dependencies:')
        print('  pip install --upgrade openai httpx')
        return 8


if __name__ == '__main__':
    sys.exit(main())
