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
- [X] Convert the whole code to FastAPI
- [X] Ensure all pages, backend code and logic works properly 
- [X] Transition to PostgreSQL database
- [X] Create backend for saving all data into db
- [X] Integrate course_info.md (all of this content is saved as base64 and displayed)
- [X] Integrate course.yaml for information displayed on horizontal cards; this same info will be inside course_info.md but formatted 
- [X] Integrate course_structure.yaml for structure of modules, sections & exercises
- [X] Create login, register, logout with usernames alone (for testing)
- [X] Create admin user
	- [X] Show a different area for admins when they login, for example course upload is only visible to admins 
- [ ] add strict cookies & auth token that expires quickly after use 
- [ ] Create dashboard for users to show progress on all courses that you have started, your total points 
- [X] Create account deletion page; disable it for admin 
- [X] Before login should only sign up / sign in forms 
- [X] Restrict course uploading to a specific user (e.g. admin)
	- [X] Test it again
- [ ] Make the navbar responsive; burger icons don't work on small screens 
- [ ] User profile must show total points, total completed modules, sections, exercises; it must also list all completed things like modules, sections, exercises along with points you earn for them and timestamp 
- [ ] When doing a section, the sidebar should only show chapters & sections for that module
	- [ ] Each module can be done any time and they will have its own progress bar that will show on course review page 
- [ ] Horizontal course card must have info from course_intro.yaml && two buttons, one to show "Course Information" and another one to "View course"
	- [ ] Show information will show contents of course_info.md
	- [ ] `View course` will show each module on a horizontal card with description and `View` button and it will show a progress bar
	- [ ] Additionally this page will show a base progress bar that calculates score from all modules within that course; all points too 
- [ ] Add dim mode to create an overlay on site for night mode 
- [ ] Create search & filter for courses so that you can search for courses by name & filter them by one or multiple topics & by default show only English courses but add options to show courses in other languages 
	- [ ] Create the same course in French
	- [ ] Ensure it works 
- [ ] Create overview page for every course, this will contain contents of creator.yaml in a very beautified manner

---

- [ ] Add logs for all actions 
- [ ] Add strict CSP rules & localize everything 
- [ ] Add appropriate messages for when you finish courses & stuff
- [ ] Add a proper changelog, security.md 
- [ ] Create visual profiles, progress bar for all courses, progress and badges for user
- [ ] Add a badges sections for the badges you earn when you complete a course 
- [ ] Create proper security headers, robots.txt & security.txt and SECURITY.md 
- [ ] When you click "Mark as completed", the app must take you to the next section, chapter or if it's course's end, to the badge
- [ ] The container moves to the left while viewing a section, fix that
- [ ] Add round green check mark for sections/exercises/modules you complete when doing a section/exercise; this same thing should show on course itself  
- [ ] When you open a section and select code of that section with mouse, the container enlarges, fix this
- [ ] When adding OAuth, ensure that admin isn't affected

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



