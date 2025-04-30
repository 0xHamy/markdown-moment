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


