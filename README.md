# Simple site for uploading Markdown courses

> ⚠️ Attention<br>This repository is under maintenance.

# Todo
- [ ] Convert the whole code to FastAPI & use the PostgreSQL database
- [ ] Create proper security headers, robots.txt & security.txt and SECURITY.md 
- [ ] Create proper display for course.yaml
- [ ] Create horizontal cards for showing courses 
- [ ] Create dashboard to show progress and list of ongoing courses and the ones you have in-progress, your points and the last time you did a challenge 
- [ ] Create login, register, logout with usernames alone 
- [ ] Add settings to set default language so that all material is displayed in that language 
- [ ] Create visual profiles, progress bar for all courses, progress and badges for user
- [ ] Create account deletion page
- [ ] Add appropriate messages for when you finish courses & stuff
- [ ] Add a badges sections for the badges you earn when you complete a course 
- [ ] Add horizontal containers to show all courses, their info and some contents of creator.yaml; course image, name, description, sections, exercises, modules; read more 
- [ ] Create overview page for every course, this will contain contents of creator.yaml in a very beautified manner
- [ ] When you click "Mark as completed", the app must take you to the next section, chapter or if it's course's end, to the badge
- [ ] The container moves to the left while viewing a section, fix that
- [ ] Restrict course uploading to a specific user (e.g. admin)
- [ ] Before login should only sign up / sign in forms 
- [ ] Add round green check mark for sections/exercises/modules you complete when doing a section/exercise; this same thing should show on course itself  
- [ ] When you open a section and select code of that section with mouse, the container enlarges, fix this


The `creator.yaml` will be used to specify all of the following:
1. Course title
2. Course image 
3. Course badge 
4. Course version 
5. Languages (e.g. English & French)
6. Author(s), Co-Author(s), Editors(s), Technical reviewer(s)
	1. Name, short bio, job role, country, contacts 
7. Course settings
	1. Duration (in hours, because cyber moves fast, we don't have time)
	2. Difficulty 
	3. Type (e.g. Crash, foundations, masterclass)
	4. Level (e.g. 1)
8. Prerequisite 
	1. A list of things
9. Topics discussed in a course (e.g. LLMs, Python, JS)
10. Course reviews by other experts 


The `course.yaml` will contain structure for modules, sections, exercises & points. 
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
- Create backend for admin to login & upload courses; all dangerous actions will require OTP & multiple confirmations (re-login)
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


the updates from github are all performed manually and when you create an update, a new copy of that course is made, this temporary copy could be compared with the previous course and also viewed in preview to ensure everything works. 

Updates are not automated because we tend to review courses carefully before shipping them.



