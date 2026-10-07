import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'

freelancer_skills = db.Table('freelancer_skills',
 db.Column('profile_id', db.Integer, db.ForeignKey('freelancer_profile.id'), primary_key=True),
 db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True),
 db.Column('verified', db.Boolean, default=False, nullable=False))
project_skills = db.Table('project_skills',
 db.Column('request_id', db.Integer, db.ForeignKey('project_request.id'), primary_key=True),
 db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True))

class User(UserMixin, db.Model):
 id=db.Column(db.Integer, primary_key=True); name=db.Column(db.String(100), nullable=False); email=db.Column(db.String(160), unique=True, nullable=False); password_hash=db.Column(db.String(255), nullable=False); role=db.Column(db.String(20), default='client'); active=db.Column(db.Boolean, default=True); created_at=db.Column(db.DateTime, default=datetime.utcnow)
 profile=db.relationship('FreelancerProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
 def set_password(self,p): self.password_hash=generate_password_hash(p)
 def check_password(self,p): return check_password_hash(self.password_hash,p)

class Skill(db.Model):
 id=db.Column(db.Integer, primary_key=True); name=db.Column(db.String(80), unique=True, nullable=False)

class FreelancerProfile(db.Model):
 id=db.Column(db.Integer, primary_key=True); user_id=db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False); title=db.Column(db.String(140), default='Independent professional'); bio=db.Column(db.Text, default=''); location=db.Column(db.String(100), default='India'); experience=db.Column(db.String(40), default='Intermediate'); hourly_rate=db.Column(db.Integer, default=800); available=db.Column(db.Boolean, default=True); avatar=db.Column(db.String(300), default=''); user=db.relationship('User', back_populates='profile'); skills=db.relationship('Skill', secondary=freelancer_skills, lazy='subquery'); portfolio=db.relationship('PortfolioProject', backref='profile', cascade='all, delete-orphan')

class PortfolioProject(db.Model):
 id=db.Column(db.Integer, primary_key=True); profile_id=db.Column(db.Integer, db.ForeignKey('freelancer_profile.id'), nullable=False); title=db.Column(db.String(120), nullable=False); description=db.Column(db.Text, default=''); tech=db.Column(db.String(250), default=''); link=db.Column(db.String(300), default='')

class ProjectRequest(db.Model):
 id=db.Column(db.Integer, primary_key=True); client_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False); freelancer_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False); title=db.Column(db.String(140), nullable=False); description=db.Column(db.Text, nullable=False); budget=db.Column(db.Integer, default=0); deadline=db.Column(db.String(30), default=''); status=db.Column(db.String(20), default='Pending'); created_at=db.Column(db.DateTime, default=datetime.utcnow); client=db.relationship('User', foreign_keys=[client_id]); freelancer=db.relationship('User', foreign_keys=[freelancer_id]); skills=db.relationship('Skill', secondary=project_skills)

class ContactMessage(db.Model):
 id=db.Column(db.Integer, primary_key=True); name=db.Column(db.String(100), nullable=False); email=db.Column(db.String(160), nullable=False); message=db.Column(db.Text, nullable=False); created_at=db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(uid): return db.session.get(User, int(uid))

def role_required(*roles):
 def deco(fn):
  from functools import wraps
  @wraps(fn)
  @login_required
  def wrapped(*a,**kw):
   if current_user.role not in roles: abort(403)
   return fn(*a,**kw)
  return wrapped
 return deco

def create_app():
 app=Flask(__name__); app.config['SECRET_KEY']=os.environ.get('SECRET_KEY','dev-change-this-secret'); app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('DATABASE_URL','sqlite:///'+os.path.join(BASE_DIR,'skillswap.db')); app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
 db.init_app(app); login_manager.init_app(app)
 @app.context_processor
 def common(): return {'all_skills':Skill.query.order_by(Skill.name).all(), 'skill_verified':skill_verified}
 @app.route('/')
 def home(): return render_template('home.html', featured=FreelancerProfile.query.join(User).filter(User.active.is_(True)).limit(6).all())
 @app.route('/about')
 def about(): return render_template('info.html', title='Talent that earns your trust', intro='Skill Swap helps teams find independent professionals through skills they can see and verify.', blocks=[('Skills first','Search by the work you need done.'),('Trust built in','Admins can verify skills, making relevant experience easier to compare.'),('People powered','Clear profiles and direct project requests keep collaboration simple.')])
 @app.route('/how-it-works')
 def how_it_works(): return render_template('info.html', title='A better way to find your next collaborator', intro='From a skill list to a real conversation in a few straightforward steps.', blocks=[('01 · Choose skills','Tell us what your project needs.'),('02 · Compare matches','See skill overlap and verified coverage.'),('03 · Meet your match','Explore portfolios and send a request.'),('04 · Get to work','Accept a request and move the project forward.')])
 @app.route('/browse')
 def browse():
  skills=Skill.query.order_by(Skill.name).all(); q=request.args.get('q','').strip(); skill_id=request.args.get('skill',''); verified=request.args.get('verified')=='1'; experience=request.args.get('experience',''); available=request.args.get('available')=='1'; rate=request.args.get('max_rate','')
  query=FreelancerProfile.query.join(User).filter(User.active.is_(True))
  if q: query=query.filter(or_(User.name.ilike(f'%{q}%'),FreelancerProfile.title.ilike(f'%{q}%'),FreelancerProfile.bio.ilike(f'%{q}%')))
  if skill_id.isdigit(): query=query.filter(FreelancerProfile.skills.any(Skill.id==int(skill_id)))
  if verified: query=query.filter(FreelancerProfile.id.in_(db.select(freelancer_skills.c.profile_id).where(freelancer_skills.c.verified.is_(True))))
  if experience: query=query.filter(FreelancerProfile.experience==experience)
  if available: query=query.filter(FreelancerProfile.available.is_(True))
  if rate.isdigit(): query=query.filter(FreelancerProfile.hourly_rate<=int(rate))
  return render_template('browse.html',profiles=query.all(),skills=skills)
 @app.route('/freelancer/<int:uid>')
 def freelancer(uid):
  user=User.query.get_or_404(uid)
  if not user.profile or not user.active: abort(404)
  return render_template('profile.html', person=user, profile=user.profile)
 @app.route('/register', methods=['GET','POST'])
 def register():
  if current_user.is_authenticated: return redirect(url_for('dashboard'))
  if request.method=='POST':
   name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower(); password=request.form.get('password',''); role=request.form.get('role','client')
   if not name or not email or len(password)<8 or password!=request.form.get('confirm') or role not in ('client','freelancer'): flash('Check your details. Passwords must match and have at least 8 characters.','error')
   elif User.query.filter_by(email=email).first(): flash('That email is already registered.','error')
   else:
    u=User(name=name,email=email,role=role); u.set_password(password); db.session.add(u)
    if role=='freelancer': u.profile=FreelancerProfile(title='New freelancer',bio='Tell clients what you do and the kinds of projects you enjoy.')
    db.session.commit(); login_user(u); flash('Welcome to Skill Swap!','success'); return redirect(url_for('dashboard'))
  return render_template('auth.html', mode='register')
 @app.route('/login', methods=['GET','POST'])
 def login():
  if request.method=='POST':
   u=User.query.filter_by(email=request.form.get('email','').strip().lower()).first()
   if u and u.active and u.check_password(request.form.get('password','')): login_user(u); return redirect(url_for('dashboard'))
   flash('Email or password is incorrect.','error')
  return render_template('auth.html',mode='login')
 @app.route('/logout')
 @login_required
 def logout(): logout_user(); flash('You have been signed out.','success'); return redirect(url_for('home'))
 @app.route('/dashboard')
 @login_required
 def dashboard():
  if current_user.role=='admin': return redirect(url_for('admin'))
  if current_user.role=='freelancer': return redirect(url_for('freelancer_dashboard'))
  reqs=ProjectRequest.query.filter_by(client_id=current_user.id).order_by(ProjectRequest.created_at.desc()).all(); return render_template('dashboard.html',requests=reqs,kind='client')
 @app.route('/freelancer/dashboard')
 @role_required('freelancer')
 def freelancer_dashboard():
  reqs=ProjectRequest.query.filter_by(freelancer_id=current_user.id).order_by(ProjectRequest.created_at.desc()).all(); return render_template('dashboard.html',requests=reqs,kind='freelancer')
 @app.route('/settings',methods=['GET','POST'])
 @login_required
 def settings():
  if request.method=='POST':
   current_user.name=request.form.get('name','').strip() or current_user.name
   if current_user.role=='freelancer' and current_user.profile:
    p=current_user.profile; p.title=request.form.get('title','').strip(); p.bio=request.form.get('bio','').strip(); p.location=request.form.get('location','').strip(); p.experience=request.form.get('experience','Intermediate'); p.hourly_rate=int(request.form.get('hourly_rate') or 0); p.available=bool(request.form.get('available'))
   db.session.commit(); flash('Your profile was saved.','success'); return redirect(url_for('settings'))
  return render_template('settings.html')
 @app.route('/skills',methods=['GET','POST'])
 @role_required('freelancer')
 def my_skills():
  p=current_user.profile
  if request.method=='POST':
   try: s=Skill.query.get(int(request.form.get('skill_id')))
   except (ValueError,TypeError): s=None
   if s and s not in p.skills: p.skills.append(s); db.session.commit(); flash('Skill added.','success')
   return redirect(url_for('my_skills'))
  return render_template('skills.html',profile=p)
 @app.post('/skills/<int:sid>/remove')
 @role_required('freelancer')
 def remove_skill(sid):
  s=Skill.query.get_or_404(sid); p=current_user.profile
  if s in p.skills:
   db.session.execute(freelancer_skills.delete().where(freelancer_skills.c.profile_id==p.id,freelancer_skills.c.skill_id==sid)); db.session.commit()
  return redirect(url_for('my_skills'))
 @app.route('/portfolio',methods=['GET','POST'])
 @role_required('freelancer')
 def portfolio():
  if request.method=='POST':
   title=request.form.get('title','').strip()
   if title: db.session.add(PortfolioProject(profile_id=current_user.profile.id,title=title,description=request.form.get('description',''),tech=request.form.get('tech',''),link=request.form.get('link',''))); db.session.commit(); flash('Portfolio project added.','success')
   return redirect(url_for('portfolio'))
  return render_template('portfolio.html',projects=current_user.profile.portfolio)
 @app.post('/portfolio/<int:pid>/delete')
 @role_required('freelancer')
 def delete_portfolio(pid):
  p=PortfolioProject.query.filter_by(id=pid,profile_id=current_user.profile.id).first_or_404(); db.session.delete(p); db.session.commit(); return redirect(url_for('portfolio'))
 @app.route('/request/<int:uid>',methods=['GET','POST'])
 @role_required('client')
 def new_request(uid):
  target=User.query.get_or_404(uid)
  if not target.profile or target.role!='freelancer': abort(404)
  if request.method=='POST':
   title=request.form.get('title','').strip(); desc=request.form.get('description','').strip()
   if not title or not desc: flash('Add a title and project description.','error')
   else:
    r=ProjectRequest(client_id=current_user.id,freelancer_id=uid,title=title,description=desc,budget=int(request.form.get('budget') or 0),deadline=request.form.get('deadline','')); ids=[int(x) for x in request.form.getlist('skills') if x.isdigit()]; r.skills=Skill.query.filter(Skill.id.in_(ids)).all() if ids else []; db.session.add(r); db.session.commit(); flash('Project request sent.','success'); return redirect(url_for('dashboard'))
  return render_template('request_form.html',person=target)
 @app.route('/requests/<int:rid>')
 @login_required
 def request_detail(rid):
  r=ProjectRequest.query.get_or_404(rid)
  if current_user.role!='admin' and current_user.id not in (r.client_id,r.freelancer_id): abort(403)
  return render_template('request_detail.html',item=r)
 @app.post('/requests/<int:rid>/status')
 @role_required('freelancer')
 def request_status(rid):
  r=ProjectRequest.query.get_or_404(rid)
  if r.freelancer_id!=current_user.id: abort(403)
  status=request.form.get('status')
  if status in ('Accepted','Rejected','Completed') and (status!='Completed' or r.status=='Accepted'): r.status=status; db.session.commit(); flash('Request status updated.','success')
  return redirect(url_for('freelancer_dashboard'))
 @app.route('/contact',methods=['GET','POST'])
 def contact():
  if request.method=='POST':
   name=request.form.get('name','').strip(); email=request.form.get('email','').strip(); message=request.form.get('message','').strip()
   if name and email and message: db.session.add(ContactMessage(name=name,email=email,message=message)); db.session.commit(); flash('Thanks for reaching out. We’ll be in touch.','success'); return redirect(url_for('contact'))
   flash('Please complete every field.','error')
  return render_template('contact.html')
 @app.get('/api/skills')
 def api_skills(): return jsonify([{'id':s.id,'name':s.name} for s in Skill.query.order_by(Skill.name)])
 @app.get('/api/freelancers')
 def api_freelancers(): return jsonify([serialize(p) for p in FreelancerProfile.query.join(User).filter(User.active.is_(True)).all()])
 @app.get('/api/freelancers/<int:uid>')
 def api_freelancer(uid):
  u=User.query.get_or_404(uid); return jsonify(serialize(u.profile))
 @app.post('/api/freelancers/match')
 def api_match():
  data=request.get_json(silent=True) or {}; wanted=data.get('skills',[])
  wanted_ids={int(x) for x in wanted if str(x).isdigit()}; wanted_names={str(x).strip().lower() for x in wanted if not str(x).isdigit()}; wanted_ids|={s.id for s in Skill.query.all() if s.name.lower() in wanted_names}
  if not wanted_ids: return jsonify({'results':[],'message':'Choose at least one skill to see matches.'})
  results=[]
  for p in FreelancerProfile.query.join(User).filter(User.active.is_(True),User.role=='freelancer').all():
   found=set(); verified=set()
   for s in p.skills:
    if s.id in wanted_ids:
     found.add(s.id)
     v=db.session.execute(db.select(freelancer_skills.c.verified).where(freelancer_skills.c.profile_id==p.id,freelancer_skills.c.skill_id==s.id)).scalar()
     if v: verified.add(s.id)
   if found:
    item=serialize(p); item.update(match=round(len(found)/len(wanted_ids)*100),matched=len(found),verified_count=len(verified),score=round(100*len(found)/len(wanted_ids)+10*len(verified)/len(wanted_ids),1)); results.append(item)
  results.sort(key=lambda x:(x['score'],x['match'],x['verified_count']),reverse=True); return jsonify({'results':results})
 @app.post('/api/project-requests')
 @role_required('client')
 def api_request():
  data=request.get_json(silent=True) or {}
  try: uid=int(data.get('freelancer_id')); budget=int(data.get('budget') or 0)
  except (ValueError,TypeError): return jsonify({'error':'Invalid freelancer or budget'}),400
  u=User.query.get(uid)
  if not u or u.role!='freelancer' or not u.profile: return jsonify({'error':'Freelancer not found'}),404
  if not data.get('title') or not data.get('description'): return jsonify({'error':'Title and description are required'}),400
  r=ProjectRequest(client_id=current_user.id,freelancer_id=uid,title=data['title'],description=data['description'],budget=budget,deadline=data.get('deadline','')); db.session.add(r); db.session.commit(); return jsonify({'id':r.id,'status':r.status}),201
 @app.route('/admin')
 @role_required('admin')
 def admin(): return render_template('admin.html',users=User.query.order_by(User.created_at.desc()).all(),requests=ProjectRequest.query.order_by(ProjectRequest.created_at.desc()).all(),messages=ContactMessage.query.order_by(ContactMessage.created_at.desc()).all(),skills=Skill.query.order_by(Skill.name).all(),profiles=FreelancerProfile.query.all())
 @app.post('/admin/skill')
 @role_required('admin')
 def add_skill():
  name=request.form.get('name','').strip()
  if name and not Skill.query.filter_by(name=name).first(): db.session.add(Skill(name=name)); db.session.commit(); flash('Skill created.','success')
  return redirect(url_for('admin'))
 @app.post('/admin/skill/<int:sid>/edit')
 @role_required('admin')
 def edit_skill(sid):
  skill=Skill.query.get_or_404(sid); name=request.form.get('name','').strip()
  if name and not Skill.query.filter(Skill.name==name,Skill.id!=sid).first(): skill.name=name; db.session.commit(); flash('Skill updated.','success')
  return redirect(url_for('admin'))
 @app.post('/admin/skill/<int:sid>/delete')
 @role_required('admin')
 def delete_skill(sid):
  s=Skill.query.get_or_404(sid); db.session.execute(freelancer_skills.delete().where(freelancer_skills.c.skill_id==sid)); db.session.execute(project_skills.delete().where(project_skills.c.skill_id==sid)); db.session.delete(s); db.session.commit(); return redirect(url_for('admin'))
 @app.post('/admin/verify')
 @role_required('admin')
 def verify():
  uid=int(request.form['user_id']); sid=int(request.form['skill_id']); value=request.form.get('verified')=='1'; p=FreelancerProfile.query.filter_by(user_id=uid).first(); s=Skill.query.get(sid)
  if p and s and s in p.skills: db.session.execute(freelancer_skills.update().where(freelancer_skills.c.profile_id==p.id,freelancer_skills.c.skill_id==sid).values(verified=value)); db.session.commit()
  return redirect(url_for('admin'))
 @app.post('/admin/user/<int:uid>/toggle')
 @role_required('admin')
 def toggle_user(uid):
  u=User.query.get_or_404(uid)
  if u.id!=current_user.id: u.active=not u.active; db.session.commit()
  return redirect(url_for('admin'))
 @app.errorhandler(403)
 def forbidden(e): return render_template('error.html',code=403,message='You do not have access to this page.'),403
 @app.errorhandler(404)
 def missing(e): return render_template('error.html',code=404,message='We couldn’t find that page.'),404
 @app.errorhandler(500)
 def server_error(e): db.session.rollback(); return render_template('error.html',code=500,message='Something went wrong. Please try again.'),500
 with app.app_context(): db.create_all(); seed()
 return app

def skill_verified(profile, skill):
 if not profile or not skill: return False
 return bool(db.session.execute(db.select(freelancer_skills.c.verified).where(freelancer_skills.c.profile_id==profile.id,freelancer_skills.c.skill_id==skill.id)).scalar())

def serialize(p):
 if not p: return {}
 u=p.user; skills=[]
 for s in p.skills:
  v=db.session.execute(db.select(freelancer_skills.c.verified).where(freelancer_skills.c.profile_id==p.id,freelancer_skills.c.skill_id==s.id)).scalar()
  skills.append({'id':s.id,'name':s.name,'verified':bool(v)})
 return {'id':u.id,'name':u.name,'title':p.title,'bio':p.bio,'location':p.location,'experience':p.experience,'hourly_rate':p.hourly_rate,'available':p.available,'skills':skills,'portfolio':[{'title':x.title,'description':x.description,'tech':x.tech,'link':x.link} for x in p.portfolio]}

def seed():
 if Skill.query.first(): return
 names=['Python','Java','JavaScript','Flask','React','SQL','UI/UX','Figma','Photoshop','Data Analysis','Machine Learning','Content Writing','Django','HTML/CSS','Node.js','Product Design','Illustration','SEO']
 skills={n:Skill(name=n) for n in names}; db.session.add_all(skills.values()); db.session.flush()
 people=[('Aarav Sharma','Python & Flask Developer','I build dependable web products and APIs for early-stage teams.','Bengaluru','Intermediate',850,['Python','Flask','SQL','JavaScript','HTML/CSS']),('Mira Kapoor','Product designer & researcher','Turning complex product problems into clear, friendly interfaces.','Mumbai','Advanced',1400,['UI/UX','Figma','Product Design','Illustration']),('Rohan Iyer','Data analyst','I help teams make confident decisions with clean data and useful dashboards.','Chennai','Intermediate',1100,['Python','SQL','Data Analysis','Machine Learning']),('Ananya Das','Full-stack developer','Thoughtful, accessible web experiences from database to browser.','Kolkata','Advanced',1600,['JavaScript','React','Node.js','SQL','HTML/CSS']),('Kabir Mehta','Brand & visual designer','Distinctive identities and practical design systems for growing brands.','Pune','Intermediate',1200,['Figma','Photoshop','UI/UX','Illustration']),('Zoya Khan','Content strategist','Research-led content that sounds human and helps customers take action.','Delhi','Advanced',950,['Content Writing','SEO']),('Ishaan Rao','Backend engineer','Reliable Python services, integrations, and database design.','Hyderabad','Advanced',1800,['Python','Flask','Django','SQL']),('Diya Nair','Frontend developer','Fast, polished interfaces with a focus on accessibility.','Kochi','Intermediate',1000,['JavaScript','React','HTML/CSS','Figma']),('Arjun Patel','ML engineer','Practical machine learning and data pipelines for real-world teams.','Ahmedabad','Advanced',2000,['Python','Machine Learning','Data Analysis','SQL']),('Sara Fernandes','UX/UI designer','I partner with founders to make products easier to understand and use.','Goa','Intermediate',1250,['UI/UX','Figma','Product Design'])]
 for i,(name,title,bio,loc,exp,rate,sk) in enumerate(people):
  u=User(name=name,email=f'demo{i+1}@skillswap.local',role='freelancer'); u.set_password('demo1234'); p=FreelancerProfile(title=title,bio=bio,location=loc,experience=exp,hourly_rate=rate,available=i!=5); u.profile=p; db.session.add(u); db.session.flush()
  for n in sk: p.skills.append(skills[n])
  if i in (0,1,2,6,8):
   db.session.flush()
   for s in p.skills[:min(3,len(p.skills))]: db.session.execute(freelancer_skills.update().where(freelancer_skills.c.profile_id==p.id,freelancer_skills.c.skill_id==s.id).values(verified=True))
  db.session.add(PortfolioProject(profile=p,title=['Learning platform API','Mobile banking redesign','Retail insights dashboard'][i%3],description='A focused project delivered with a small, collaborative team.',tech=', '.join(sk[:3]),link=''))
 for name,email,role in [('Demo Client','client@skillswap.local','client'),('Site Admin','admin@skillswap.local','admin')]:
  u=User(name=name,email=email,role=role); u.set_password('demo1234'); db.session.add(u)
 db.session.commit()
 client=User.query.filter_by(email='client@skillswap.local').first(); f=User.query.filter_by(email='demo1@skillswap.local').first(); db.session.add(ProjectRequest(client_id=client.id,freelancer_id=f.id,title='Build a course booking API',description='Create a small Flask API for course listings, booking, and email notifications.',budget=35000,deadline='2026-11-30')); db.session.commit()

app=create_app()
if __name__=='__main__': app.run(debug=True)

