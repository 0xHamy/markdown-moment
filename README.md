# Simple site for uploading Markdown courses

> ⚠️ Attention<br>This repository is under maintenance.

## Tech-stack
- **Frontend:**
	- TailwindCSS 4.x
	- HTML5
	- jQuery
- **Backend:**
	- FastAPI
- **Database:**
	- PostgreSQL
	- A logging system for logs
- **Deployment:**
	- Docker

---

# Todo
- [ ] Ensure that HTML is also supported for course overview because this page is going to have custom HTML (tailwindcss) styles 
- [ ] Make the navbar responsive; burger icons don't work on small screens 
	- [ ] remove the sidebar from base.html and put it inside section.html 
- [ ] Modify `academy/course/1/info/` to show course_id instead of 1
	- [ ] Modify the page and correct all stylings 
	- [ ] Remove the x/close icon and functionality 
	- [ ] ensure the page is responsive 
- [ ] Viewing a course
	- [ ] Display all modules in horizontal cards with holo circle (green-checked if module was completed), title, description, view button, progress bar to show how many items were done 
	- [ ] Display total progress bar, display coints for exercises, sections, modules in this format: 0/1 Exercises 0/20 Sections 0/8 Modules
	- [ ] Course status: ongoing, not started, completed 
- [ ] Viewing a module
	- [ ] Clicking view on a module will open the first section of that module, which is usually an overview 
	- [ ] Open up the sidebar to the left, display all content with hallow circle icon, fill it when a section or exercise or module is completed
	- [ ] Every module will have an overview page that will be opened first 
- [ ] Add appropriate messages for when you finish a section, a module or an entire course
- [ ] When you click "Mark as completed", the app must take you to the next section, chapter or if it's course's end, to the badge
- [ ] Ensure that translation is also available for those horizontal cards that show when you select a different language of the course OR for the course review
---

- [ ] User profile must show total points, total completed modules, sections, exercises; it must also list all completed things like modules, sections, exercises along with points you earn for them and timestamp 
- [ ] Add dim mode to create an overlay on site for night mode 
- [ ] Create search & filter for courses so that you can search for courses by name & filter them by one or multiple topics & by language
	- [ ] Create the same course in French
	- [ ] Ensure language switch works 
- [ ] Add video support to course; videos can uploaded just like images
- [ ] Add custom HTML support to markdown too so that you can stylize course_intro.md
- [ ] Add logs for all actions 
- [ ] add strict cookies & auth token that expires quickly after use 
- [ ] Add strict CSP rules & localize everything 
- [ ] Add a badges sections for the badges you earn when you complete a course 
- [ ] Create proper security headers, robots.txt & security.txt and SECURITY.md, changelog
- [ ] When adding OAuth, ensure that admin isn't affected


---

The `course_intro.yaml` will be used to specify all of the following:
1. Course title
3. Course badge 
4. Course version 
5. Language (This will be used for filtering between languages)
6. Course settings
	1. Duration (in hours, because cyber moves fast, we don't have time)
	2. Difficulty 
	3. Type (e.g. Crash, foundations, masterclass)
	4. Level (e.g. 1)
7. Tags


The `course_info.md` will have markdown page that would give an intro to the course, it will include all of the following:
- Everything from creator.yaml 
- Overview
- What you will learn
- Course structure
- Prerequisite
- Languages this course is available in
- Course auhtor(s), editor(s), technical reviewers, language reviewer  
- Author(s), Co-Author(s), Editors(s), Technical reviewer(s)
	- this includes name, a short bio, and a primary contact (e.g. LinkedIn)
- Course reviews
- Thanks

The `course_structure.yaml` will contain structure for modules, sections, exercises & points. 
1. Course structure 
	1. Modules & points for every module
	2. Sections & points for every section
	3. Exercises & points for every exercise
	4. The structure is going to be like a custom table of contents with links to the markdown pages & media 


Before login, the subdomain will have a top nav with these items:
- Preview courses; shows all courses, their modules, sections but not content 
- Login page
- Register page


The `academy.cyberm.ca` **AFTER LOGIN** will have a hidden navbar on top with these items:
- Username; opens settings; language change 
- Courses; opens all courses 
- Progress; opens all in-progress and finished courses with filters 
- Dim switch (far left side)

Courses will contain all courses with filters and search available to see:
- crash courses, foundations or masterclass 
- search by topic (one or multiple can be selected)
- search by language (English or French)


### Backend for uploading courses
- Create backend for admin to login & upload courses; all dangerous actions will require OTP & multiple confirmations such as re-login with OAuth 
- Create functionality to upload courses as zip or import them via a Github link; for private repos allow using access tokens; we must be able to select a specific commit or branch too 
- Create a beautiful table to show all uploaded courses, their current commit number, last update, view, status 
- You can't just update a course by clicking update, selecting a new zip and viola 
    - You have to first upload a course, it will be hidden and saved as "under_review" course (published, under review, retired)
    - Later, when you want to update, you select from the list of already uploaded courses to replace any old version with the new version 
    - These steps are mandatory to ensure that these actions are taken seriously 
- To maintain accuracy, you have to upload specific language versions for every course 
- Course delete option is available too but it courses can't be deleted UNLESS they are retired
	- When a course is retired, it becomes available for deletion
	- When a course is retired, it becomes hidden 
- Notification system
	- Alert admins whenever a change is made via SMS 
- Security 
	- Implement strict one type use cookies and auth token for all actions 
	- Perform force logout after 5 minute of inactivity 
- admin login will also require VPN access to the server 


the updates from github are all performed manually and when you create an update, a new copy of that course is made, this temporary copy could be compared with the previous course and also viewed in preview to ensure everything works. 

Updates are not automated because we tend to review courses carefully before shipping them.



