# Railway Deployment Checklist

## Pre-Deployment

- [ ] Code pushed to GitHub repository
- [ ] All dependencies listed in requirements.txt
- [ ] .env.example file created (DO NOT commit .env)
- [ ] Procfile created
- [ ] railway.json configured
- [ ] Database models tested locally

## Railway Setup

- [ ] Create Railway account at https://railway.app
- [ ] Create new project
- [ ] Connect GitHub repository
- [ ] Add PostgreSQL database service
- [ ] Note the DATABASE_URL (automatically provided)

## Environment Variables

In Railway project → Variables, add:

- [ ] `SECRET_KEY` - Generate with: `python generate_secret_key.py`
- [ ] `FLASK_ENV=production`
- [ ] `DATABASE_URL` - Auto-provided by Railway PostgreSQL

## Database Initialization

In Railway terminal:

- [ ] Run migrations: `flask db upgrade`
- [ ] Create admin user (see QUICKSTART.md for command)
- [ ] Verify tables created

## Domain Configuration

### Railway Setup
- [ ] Go to Settings → Domains
- [ ] Add custom domain
- [ ] Copy CNAME/A record values

### Hostinger DNS Setup
- [ ] Login to Hostinger
- [ ] Go to domain DNS management
- [ ] Add CNAME record for www subdomain
- [ ] Add A record for root domain (optional)
- [ ] Wait 24-48 hours for propagation

### SSL Certificate
- [ ] Railway auto-provisions SSL
- [ ] Verify HTTPS works after DNS propagation

## Post-Deployment Testing

- [ ] Visit deployed URL
- [ ] Test public application form at `/apply`
- [ ] Login as admin at `/auth/login`
- [ ] Create a test rep user
- [ ] Approve a test application
- [ ] Create line of credit
- [ ] Assign deal to rep
- [ ] Test rep login and dashboard
- [ ] Test customer login portal
- [ ] Verify email notifications work (if configured)

## Security Checklist

- [ ] Strong SECRET_KEY in production
- [ ] Default admin password changed
- [ ] .env file NOT committed to git
- [ ] HTTPS enabled (automatic with Railway)
- [ ] Database backups configured (Railway automatic)
- [ ] Error pages configured
- [ ] Rate limiting considered for forms

## Monitoring

- [ ] Check Railway deployment logs
- [ ] Monitor database usage
- [ ] Set up error notifications
- [ ] Test application regularly

## Custom Domain Verification

Test these URLs work:
- [ ] http://yourdomain.com → redirects to https
- [ ] https://yourdomain.com → works
- [ ] https://www.yourdomain.com → works
- [ ] /apply form loads correctly
- [ ] /auth/login works
- [ ] /auth/customer-login works

## Common Issues & Solutions

### Issue: "Application Error"
- Check Railway logs
- Verify environment variables are set
- Ensure database migrations ran successfully

### Issue: "Database connection failed"
- Verify DATABASE_URL is set
- Check PostgreSQL service is running
- Try redeploying

### Issue: "404 on custom domain"
- Wait for DNS propagation (24-48 hours)
- Verify CNAME record is correct
- Check Railway domain settings

### Issue: "Static files not loading"
- Railway serves static files automatically
- Check file paths in templates
- Verify bootstrap CDN links work

## Maintenance

Regular tasks:
- [ ] Update dependencies monthly
- [ ] Review and backup database weekly
- [ ] Monitor application performance
- [ ] Check for security updates
- [ ] Review user feedback

## Support Resources

- Railway Docs: https://docs.railway.app
- Flask Docs: https://flask.palletsprojects.com
- PostgreSQL Docs: https://www.postgresql.org/docs/

## Notes

- Railway provides automatic SSL certificates
- Database backups are automatic on Railway
- PostgreSQL connection pooling is handled by Railway
- Railway auto-restarts on errors (configured in railway.json)
