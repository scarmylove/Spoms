# SPOMS - Vercel Deployment Guide

## Overview

This guide explains how to deploy the SPOMS (Supplier and Purchase Order Management System) to Vercel with MongoDB as the database backend.

## Key Changes for Cloud Deployment

### 1. Database Migration (JSON → MongoDB)
- **Before**: Used JSON files stored locally (`data/*.json`)
- **After**: Uses MongoDB Atlas (cloud database)
- **Reason**: Vercel's serverless filesystem is ephemeral (temporary); files don't persist between deployments

### 2. Configuration Management
- **Before**: Hardcoded secrets in `app.py`
- **After**: Uses environment variables for security
- **Files**: `config.py`, `.env.example`, `vercel.json`

### 3. Python Dependencies
All required packages are listed in `requirements.txt`

## Prerequisites

1. **MongoDB Atlas Account** (Free tier available)
   - Create account at: https://www.mongodb.com/cloud/atlas
   - Create a new cluster
   - Generate connection string

2. **Vercel Account**
   - Sign up at: https://vercel.com
   - Connect your GitHub repository

3. **Git Repository**
   - Push code to GitHub, GitLab, or similar

## Step-by-Step Deployment

### Step 1: Set Up MongoDB Atlas Database

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new project
3. Create a new Cluster (M0 Free tier recommended)
4. Create a database user:
   - Username: `spoms_user`
   - Password: Generate a strong password
5. Add IP Whitelist: `0.0.0.0/0` (for Vercel)
6. Get connection string:
   - Click "Connect" → "Connect your application"
   - Copy the URI (should look like):
     ```
     mongodb+srv://spoms_user:password@cluster.mongodb.net/spoms?retryWrites=true&w=majority
     ```

### Step 2: Local Environment Setup

1. Create `.env` file in project root:
   ```bash
   MONGODB_URI=mongodb+srv://spoms_user:password@cluster.mongodb.net/spoms?retryWrites=true&w=majority
   FLASK_ENV=production
   SECRET_KEY=your-super-secret-key-generate-random-string
   DEBUG=False
   ```

2. Install dependencies locally:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize database (local):
   ```bash
   python init_db.py
   ```

### Step 3: Configure Vercel

1. Push code to GitHub repository
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "New Project"
4. Import your Git repository
5. Configure project:
   - Framework: "Other"
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)

6. Add Environment Variables:
   - Click "Add Environment Variable"
   - Add each variable from your `.env`:
     - `MONGODB_URI`: Your MongoDB connection string
     - `FLASK_ENV`: `production`
     - `SECRET_KEY`: Generate a random secret key
     - `DEBUG`: `False`

7. Click "Deploy"

### Step 4: Initialize Database on Vercel

After initial deployment, initialize the database:

1. You can either:
   - Run initialization locally with production MongoDB URI
   - Or contact support to run migrations

2. Users will be automatically created on first initialization with the default credentials:
   - Admin: `dennis` / `lopez`
   - Purchasing Officer: `jani` / `jani`
   - Finance Officer: `angel` / `angel`
   - Store Owner: `jennifer` / `jennifer`

## Project Structure

```
SPOMS/
├── app.py                 # Main Flask application (refactored for MongoDB)
├── config.py              # Configuration management
├── database.py            # MongoDB connection and operations
├── init_db.py             # Database initialization script
├── requirements.txt       # Python dependencies
├── vercel.json            # Vercel configuration
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── README.MD              # Project documentation
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
└── data/                  # Local JSON files (not used in production)
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/spoms` |
| `FLASK_ENV` | Flask environment | `production` |
| `SECRET_KEY` | Secret key for sessions | Random 32+ character string |
| `DEBUG` | Debug mode | `False` (for production) |
| `SESSION_TYPE` | Session storage type | `filesystem` |

## Important Security Notes

⚠️ **CRITICAL SECURITY SETTINGS:**

1. **Change Default Passwords**
   - After first login, change all default passwords
   - Use strong, unique passwords

2. **Secret Key**
   - Generate a strong random secret key
   - Never commit it to version control
   - Only store in Vercel environment variables

3. **MongoDB**
   - Use IP whitelist: `0.0.0.0/0` for Vercel (or specific IPs if possible)
   - Use strong database user password
   - Enable encryption at rest (MongoDB Free tier)

4. **HTTPS**
   - Vercel provides HTTPS automatically
   - Set `SESSION_COOKIE_SECURE = True` in production

## Troubleshooting

### Database Connection Error
```
Error: MONGODB_URI environment variable not set
```
**Solution**: Check Vercel environment variables are correctly set

### Permission Denied Error
```
Error: pymongo.errors.OperationFailure
```
**Solution**: Verify MongoDB user credentials and IP whitelist

### No Data After Deployment
```
Orders, suppliers, etc. are empty
```
**Solution**: Run `init_db.py` to populate initial data

### Session/Login Issues
```
Login fails or session clears immediately
```
**Solution**: Verify `SECRET_KEY` is set and consistent

## Monitoring

### Vercel Logs
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. View "Deployments" → "Functions" for real-time logs

### MongoDB Monitoring
1. Go to MongoDB Atlas Dashboard
2. View "Metrics" for database performance
3. Check "Activity" for operations

## Performance Optimization

For better performance on Vercel:

1. **Database Indexes** - Already created in `database.py`
2. **Query Optimization** - Use indexed fields for filtering
3. **Caching** - Consider implementing Redis caching (future)
4. **CDN** - Vercel automatically serves static files via CDN

## Updating Code

After making changes:

```bash
# Test locally
python app.py

# Commit and push
git add .
git commit -m "Update features"
git push

# Vercel automatically deploys on push to main branch
```

## Rollback

To rollback to a previous version in Vercel:

1. Dashboard → Select project
2. Click "Deployments"
3. Find the previous working version
4. Click "..." → "Redeploy"

## Getting Help

- **Vercel Documentation**: https://vercel.com/docs
- **MongoDB Documentation**: https://docs.mongodb.com
- **Flask Documentation**: https://flask.palletsprojects.com

## Next Steps

After deployment:

1. ✅ Test all features in production
2. ✅ Monitor logs for errors
3. ✅ Set up backup strategy for MongoDB
4. ✅ Train users on production access
5. ✅ Document any custom configurations

---

**Last Updated**: April 2026  
**Version**: 1.0  
**Status**: Production Ready
