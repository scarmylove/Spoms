# SPOMS Vercel Deployment Checklist

## ✅ Pre-Deployment Requirements

### System Setup
- [ ] Python 3.9+ installed locally
- [ ] Git installed and configured
- [ ] GitHub/GitLab account created
- [ ] Vercel account created
- [ ] MongoDB Atlas account created

### Project Files
- [ ] `requirements.txt` - Contains all Python dependencies
- [ ] `vercel.json` - Vercel configuration file
- [ ] `config.py` - Configuration management
- [ ] `database.py` - MongoDB connection layer
- [ ] `app.py` - Refactored for MongoDB
- [ ] `init_db.py` - Database initialization script
- [ ] `.env.example` - Environment variables template
- [ ] `.gitignore` - Git ignore rules
- [ ] Error templates: `404.html`, `500.html`

### Dependencies Installed
- [ ] Flask==2.3.3
- [ ] pymongo==4.5.0
- [ ] python-dotenv==1.0.0
- [ ] Werkzeug==2.3.7
- [ ] gunicorn==21.2.0

## 🔐 Security Pre-Checks

### Credentials & Secrets
- [ ] Generate new `SECRET_KEY` (use `os.urandom(32).hex()` in Python)
- [ ] Default user passwords UNCHANGED in code
- [ ] MongoDB password is strong (20+ characters, mix of types)
- [ ] `.env` file added to `.gitignore`
- [ ] No credentials in `vercel.json`

### MongoDB Setup
- [ ] Cluster created in MongoDB Atlas
- [ ] Database user created with strong password
- [ ] IP whitelist includes `0.0.0.0/0` (for Vercel)
- [ ] Connection string copied correctly
- [ ] Connection string format: `mongodb+srv://user:password@cluster.mongodb.net/spoms?retryWrites=true&w=majority`

## 📋 Vercel Configuration

### Environment Variables Set
- [ ] `MONGODB_URI` - MongoDB connection string
- [ ] `FLASK_ENV` - Set to `production`
- [ ] `SECRET_KEY` - Generated random key
- [ ] `DEBUG` - Set to `False`
- [ ] `SESSION_TYPE` - Set to `filesystem`

### Vercel Project Settings
- [ ] Python runtime: 3.11
- [ ] Build command: Empty (or use default)
- [ ] Output directory: (leave default)
- [ ] Root directory: `./`
- [ ] Auto-deploy on push: Enabled

## 🧪 Local Testing

### Before Deployment
- [ ] Run `pip install -r requirements.txt`
- [ ] Create local `.env` with test MongoDB URI
- [ ] Run `python init_db.py` - Check for errors
- [ ] Start app: `python app.py`
- [ ] Test login with default credentials:
  - Username: `dennis` → Password: `lopez`
  - Username: `jani` → Password: `jani`
  - Username: `angel` → Password: `angel`
  - Username: `jennifer` → Password: `jennifer`
- [ ] Test core functions:
  - [ ] Dashboard loads with statistics
  - [ ] Can view suppliers
  - [ ] Can create new supplier
  - [ ] Can view orders
  - [ ] Can view payments
  - [ ] Can submit feedback
  - [ ] Can view reports
- [ ] Check for console errors (browser dev tools)
- [ ] Test file uploads (logo, background, profile picture)
- [ ] Test user management (admin only)

## 📦 Git & Repository

### Before Push
- [ ] Repository initialized: `git init`
- [ ] Remote added: `git remote add origin <url>`
- [ ] `.gitignore` includes:
  - [ ] `.env` files
  - [ ] `__pycache__/`
  - [ ] `*.pyc`
  - [ ] `venv/`
  - [ ] `data/` (JSON files)
- [ ] No credentials in any committed files
- [ ] All required files committed:
  ```bash
  git add -A
  git commit -m "Initial SPOMS Vercel deployment"
  git push origin main
  ```

## 🚀 Vercel Deployment

### Deploy Steps
1. [ ] Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. [ ] Click "New Project"
3. [ ] Import GitHub repository
4. [ ] Configure environment variables (see checklist above)
5. [ ] Click "Deploy"
6. [ ] Wait for deployment to complete
7. [ ] Check deployment logs for errors
8. [ ] Note the Vercel URL (e.g., `https://spoms.vercel.app`)

### Post-Deployment Verification
- [ ] Website is accessible at Vercel URL
- [ ] HTTPS certificate is valid
- [ ] Homepage loads correctly
- [ ] Login page loads
- [ ] Try login with `dennis` / `lopez`
- [ ] Dashboard loads with stats
- [ ] Static files load (CSS, images, JS)
- [ ] Check browser console for errors
- [ ] Check Vercel function logs for errors

## 🗄️ Database Initialization

### Initialize MongoDB
1. [ ] One of the following:
   - [ ] Option A: Run locally with production URI:
     ```bash
     # Update .env with production MONGODB_URI
     python init_db.py
     ```
   - [ ] Option B: Contact admin to run initialization
   
2. [ ] Verify initialization:
   - [ ] Open MongoDB Atlas dashboard
   - [ ] Check `spoms` database exists
   - [ ] Check collections created:
     - [ ] `users` - Should have 4 default users
     - [ ] `suppliers` (empty initially)
     - [ ] `orders` (empty initially)
     - [ ] `payments` (empty initially)
     - [ ] `feedback` (empty initially)
     - [ ] `settings` (contains system settings)

## 🧑‍💼 Post-Deployment Tasks

### User Management
- [ ] [ **URGENT** ] Change default passwords for:
  - [ ] `dennis` (Admin)
  - [ ] `jani` (Purchasing Officer)
  - [ ] `angel` (Finance Officer)
  - [ ] `jennifer` (Store Owner)

### System Configuration
- [ ] Update system settings:
  - [ ] System name
  - [ ] Upload logo
  - [ ] Upload homepage background
- [ ] Test all features end-to-end
- [ ] Create new user accounts as needed
- [ ] Test role-based access controls

### Monitoring Setup
- [ ] Set up Vercel notifications (optional)
- [ ] Enable MongoDB alerts (optional)
- [ ] Create a monitoring dashboard
- [ ] Document support contact info

## 📊 Performance Verification

- [ ] Page load time < 3 seconds
- [ ] API responses < 1 second
- [ ] No console errors
- [ ] No unhandled promise rejections
- [ ] Database queries are efficient
- [ ] Images optimized and loading quickly

## 📝 Documentation

- [ ] [ ] DEPLOYMENT_GUIDE.md created
- [ ] [ ] README.MD updated with deployment info
- [ ] [ ] Document MongoDB connection string location
- [ ] [ ] Document Vercel project URL
- [ ] [ ] Create user access instructions
- [ ] [ ] Create admin guide for maintenance

## 🔍 Final Review

### Code Quality
- [ ] No hardcoded credentials
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Database indexes created
- [ ] Security headers present

### Functionality
- [ ] All routes working
- [ ] All APIs responding
- [ ] File uploads working
- [ ] Session management working
- [ ] Role-based access control working

### Deployment
- [ ] Green deployment status
- [ ] No error logs
- [ ] Database connected
- [ ] All environment variables set
- [ ] Backups configured (if possible)

## 📞 Support & Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Database connection error | Check MONGODB_URI in Vercel env vars |
| 502 Bad Gateway | Check Vercel logs, restart deployment |
| Static files not loading | Check static file paths, clear cache |
| Login fails | Verify user exists in DB, check password hash |
| CORS errors | Add CORS headers if needed for APIs |

### Get Help
- [ ] Vercel Docs: https://vercel.com/docs
- [ ] MongoDB Docs: https://docs.mongodb.com
- [ ] Flask Docs: https://flask.palletsprojects.com
- [ ] PyMongo Docs: https://pymongo.readthedocs.io

## ✨ Go Live!

Once all items are checked:

1. **Announce Launch**
   - [ ] Notify all users
   - [ ] Share Vercel URL
   - [ ] Provide access credentials
   - [ ] Post support contact info

2. **Monitor Closely**
   - [ ] First 24 hours - Check logs frequently
   - [ ] First week - Monitor for issues
   - [ ] Ongoing - Regular backups and monitoring

3. **Gather Feedback**
   - [ ] Ask users for feedback
   - [ ] Monitor error logs
   - [ ] Fix issues promptly
   - [ ] Update documentation

---

**Deployment Status**: ⏳ Pending  
**Go-Live Date**: _______________  
**Deployed By**: _______________  
**Notes**: 

