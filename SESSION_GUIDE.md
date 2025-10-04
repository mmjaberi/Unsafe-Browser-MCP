# 🔐 Session Management Guide

## Understanding Sessions

### What Gets Saved
When you save a session, the following are stored:
- **Cookies** (authentication tokens, preferences, etc.)
- **Cookie domains** (which websites they belong to)
- **Current URL** (the page you were on)
- **Timestamp** (when the session was saved)

### What Doesn't Get Saved
- Page content/state
- Form data
- JavaScript variables
- Open tabs

---

## 📋 Proper Workflow

### ✅ CORRECT Way to Use Sessions

```bash
# Step 1: Navigate and login
> nav https://example.com/login
> fill #username admin@test.com
> fill #password secret123
> click login_button

# Step 2: Save the session
> save-session my_login
✅ Session saved: my_login

# Step 3: Later, load and use the session
> load-session my_login
✅ Session loaded: my_login
   Cookies: 5 from 1 domains
   Domains: example.com
   Saved URL: https://example.com/dashboard
   ⚠️  Navigate to https://example.com/dashboard to use the session

# Step 4: Navigate to apply cookies
> nav https://example.com/dashboard
✅ Dashboard loaded

# Step 5: Now screenshot will show logged-in state
> screenshot logged_in.png
✅ Screenshot saved
```

### ❌ WRONG Way (What You Were Doing)

```bash
# DON'T DO THIS:
> load-session my_login
✅ Session loaded: my_login

> screenshot test.png    # ❌ Screenshot is blank!
# Why? Because you haven't navigated to any page yet!
# Cookies are loaded but browser is on a blank page
```

---

## 🚀 New Features

### 1. Auto-Navigate

Load session and automatically navigate to saved URL:

```bash
> load-session my_login -n
✅ Session loaded: my_login
   Cookies: 5 from 1 domains
   Domains: example.com  
   Saved URL: https://example.com/dashboard
   ✅ Auto-navigated to https://example.com/dashboard

# Now you're already on the page!
> screenshot ready.png
✅ Screenshot saved (shows logged-in state)
```

### 2. Session Info

View detailed information about a saved session:

```bash
> session-info my_login
📊 Session Info: my_login
  Saved at: 2025-01-15T10:30:45
  Cookies: 5
  Domains: example.com, .example.com
  URL: https://example.com/dashboard
```

### 3. Enhanced List

See session details when listing:

```bash
> list-sessions
💾 Saved sessions (3):
  - my_login (5 cookies) - https://example.com/dashboard
  - github_session (12 cookies) - https://github.com/home
  - default (0 cookies) - N/A
```

---

## 🎯 Common Use Cases

### Use Case 1: Test Logged-In Features

```bash
# Day 1: Login and save
> nav https://app.mysite.com/login
> fill #email test@example.com  
> fill #password pass123
> click submit
> save-session app_login

# Day 2: Resume testing
> load-session app_login -n
# Already logged in and on dashboard!
> click settings_button
> screenshot settings.png
```

### Use Case 2: Multiple Accounts

```bash
# Save different accounts
> nav https://site.com/login
> fill #username admin
> click login
> save-session admin_account

> nav https://site.com/login
> fill #username user1
> click login
> save-session user1_account

# Switch between accounts
> load-session admin_account -n
# Now logged in as admin

> load-session user1_account -n
# Now logged in as user1
```

### Use Case 3: Cross-Site Sessions

```bash
# Login to multiple related sites
> nav https://auth.example.com/login
> fill #username admin
> click login
> save-session example_auth

# Later, use on subdomain
> load-session example_auth
> nav https://app.example.com
# Cookies work across *.example.com domains!
```

---

## 🔍 Debugging Session Issues

### Check What Was Saved

```bash
> session-info my_session
📊 Session Info: my_session
  Saved at: 2025-01-15T10:30:45
  Cookies: 0                    # ⚠️ No cookies saved!
  Domains: 
  URL: https://example.com
```

**If cookies = 0:**
- You saved the session before logging in
- The site doesn't use cookies
- Cookies were blocked/cleared

### Verify Session Loaded

```bash
> load-session test
✅ Session loaded: test
   Cookies: 0 from 0 domains     # ⚠️ No cookies loaded!
```

**If no cookies loaded:**
- Session was saved without logging in
- Try logging in again and re-saving

### Check Cookie Domains

```bash
> session-info github_session
📊 Session Info: github_session
  Cookies: 8
  Domains: github.com, .github.com
  URL: https://github.com
```

**Make sure domain matches:**
- Saved on `github.com` → Must load on `github.com`
- Saved on `app.site.com` → Load on `app.site.com` or `*.site.com`

---

## 💡 Pro Tips

### 1. Always Check Session Info
```bash
> save-session important
> session-info important
# Verify it has cookies before closing!
```

### 2. Use Descriptive Names
```bash
# ❌ Bad
> save-session test
> save-session session1

# ✅ Good
> save-session gmail_admin_logged_in
> save-session github_personal_account
```

### 3. Test Sessions Immediately
```bash
> save-session my_test
> load-session my_test -n
# Test it works before assuming it's saved correctly!
```

### 4. Clean Up Old Sessions
```bash
> list-sessions
💾 Saved sessions (10):
  - old_test1 (0 cookies) - N/A     # Delete these
  - old_test2 (0 cookies) - N/A     # Delete these
  - working_session (5 cookies) - https://...  # Keep this
```

---

## 🛠️ Quick Reference

| Command | What It Does | Example |
|---------|--------------|---------|
| `save-session <name>` | Save current cookies + URL | `save-session my_login` |
| `load-session <name>` | Load cookies (manual nav) | `load-session my_login` |
| `load-session <name> -n` | Load + auto-navigate | `load-session my_login -n` |
| `list-sessions` | Show all sessions | `list-sessions` |
| `session-info <name>` | Show session details | `session-info my_login` |

---

## ⚠️ Common Mistakes

### Mistake 1: Screenshot Before Navigating
```bash
❌ load-session → screenshot
✅ load-session → nav → screenshot
```

### Mistake 2: Saving Before Login
```bash
❌ nav login page → save-session
✅ nav → login → save-session
```

### Mistake 3: Wrong Domain
```bash
# Saved on example.com, trying to load on different-site.com
❌ Won't work - cookies are domain-specific
```

### Mistake 4: Not Verifying
```bash
❌ save-session → assume it worked
✅ save-session → session-info → verify cookies > 0
```

---

## 🎉 Summary

**Remember the Golden Rule:**

1. **Save**: After logging in on the correct page
2. **Load**: Restores cookies only (not the page)
3. **Navigate**: Go to the website to apply cookies
4. **Use**: Now you're logged in!

**Or use auto-navigate:**
```bash
load-session my_session -n
# Done! Already on page with cookies loaded
```

---

**Updated**: January 2025  
**Version**: Enhanced v2.1
