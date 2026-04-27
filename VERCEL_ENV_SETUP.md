# Vercel Environment Variables Configuration

## For Vercel Dashboard

When deploying to Vercel, add these environment variables in Project Settings → Environment Variables:

### Required Variables

```
MONGODB_URI=mongodb+srv://spoms_user:YOUR_PASSWORD@cluster.mongodb.net/spoms?retryWrites=true&w=majority
```
Replace:
- `spoms_user` with your MongoDB username
- `YOUR_PASSWORD` with your MongoDB password
- `cluster` with your actual cluster name

```
FLASK_ENV=production
```

```
SECRET_KEY=your-random-32-character-string-here
```
Generate with: `python -c "import os; print(os.urandom(32).hex())"`

```
DEBUG=False
```

```
SESSION_TYPE=filesystem
```

---

## Local Development (.env file)

For local testing, use this `.env` file:

```
MONGODB_URI=mongodb+srv://spoms_user:YOUR_PASSWORD@cluster.mongodb.net/spoms?retryWrites=true&w=majority
FLASK_ENV=development
SECRET_KEY=your-random-32-character-string-here
DEBUG=True
SESSION_TYPE=filesystem
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=static/images
```

---

## Steps to Add Environment Variables in Vercel

1. Go to: https://vercel.com/dashboard
2. Select your SPOMS project
3. Go to: Settings → Environment Variables
4. Click "Add New"
5. Add each variable:
   - Name: `MONGODB_URI`
   - Value: `mongodb+srv://...` (your connection string)
6. Select: Production
7. Click "Save"
8. Repeat for other variables

---

## MongoDB Connection String Format

```
mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/DATABASE?retryWrites=true&w=majority
```

Example:
```
mongodb+srv://spoms_user:Super$ecurePassword123@spoms-cluster.mongodb.net/spoms?retryWrites=true&w=majority
```

---

## Getting MongoDB Credentials

1. Go to: https://www.mongodb.com/cloud/atlas
2. Create FREE account
3. Create Cluster (M0 free tier)
4. Create Database User:
   - Go to: Security → Database Access
   - Click "Add New Database User"
   - Username: `spoms_user`
   - Password: Generate secure password
   - Click "Add User"
5. Whitelist IP:
   - Go to: Security → Network Access
   - Click "Add IP Address"
   - Enter: `0.0.0.0/0` (allows Vercel)
   - Click "Confirm"
6. Get Connection String:
   - Go to: Clusters → Connect
   - Click "Connect your application"
   - Choose: Python 3.6+
   - Copy the URI
   - Replace `<password>` with your database user password

---

## Testing Connection Locally

After updating `.env`:

```bash
python init_db.py
```

If successful, you'll see:
```
==================================================
🔧 Initializing SPOMS Database
==================================================

✓ Initialized 4 users
✓ Initialized settings

==================================================
✓ Database initialization completed successfully!
==================================================
```

---

## After Deployment

1. Visit your Vercel URL
2. Login with `dennis` / `lopez`
3. Change all default passwords
4. Test all features
5. Monitor Vercel logs for errors

---

## Common Issues

### "MONGODB_URI environment variable not set"
- Check Vercel project environment variables
- Make sure variable name is exactly: `MONGODB_URI`
- Redeploy after adding variables

### "connect ECONNREFUSED"
- Check MongoDB connection string
- Verify IP whitelist includes `0.0.0.0/0`
- Check database user credentials

### "MongoServerError: E11000 duplicate key error"
- Database already initialized
- Running `init_db.py` twice (OK - it skips if data exists)

---

## Production Checklist

- [ ] MongoDB cluster created
- [ ] Database user created
- [ ] IP whitelist set to `0.0.0.0/0`
- [ ] Connection string tested locally
- [ ] `init_db.py` run successfully
- [ ] All environment variables added to Vercel
- [ ] `.env` file NOT committed to Git
- [ ] Application deployed on Vercel
- [ ] Login works with default credentials
- [ ] Default passwords changed
- [ ] All features tested
