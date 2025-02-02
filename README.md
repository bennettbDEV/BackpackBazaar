<!-- ABOUT THE PROJECT -->
## About The Project
This project, Backpack Bazaar, is an extension of a group project I worked on previously -> https://github.com/bennettbDEV/CollegeMarketplace. The goal of this project will be to: 
- Refactor the backend to use Django's ORM, which will be faster and more reliable
- Add more customization options
- Implement automatic listing classification using AI/ML
- Develop an algorithm/method to provide suggested/recommended listings to users

## Roadmap

- [X] Add dark mode
- [X] Refactor front-end to use rems instead of px
- [X] Refactor authentication using Django's built in tools
- [X] Alter User/UserProfile to use Django's ORM
- [ ] Test User/UserProfile
- [X] Alter Listing to use Django's ORM
- [X] Test Listing
- [X] Alter Messages to use Django's ORM
- [X] Test Messages
- [X] New message frontend
- [ ] Add tests for every feature
- [X] Frontend Integration
- [ ] Test Frontend more thoroughly
- [X] Add automatic listing classification
- [ ] Develop algorithm to suggest listings

## Try it out!
To install the dependencies and run the project as it is now, follow these simple steps in your terminal:

0. Prerequisites:
Install [Node.js](https://nodejs.org/en/download/package-manager)(version 20 or newer) and [Python](https://www.python.org/downloads/)(version 3.10 or newer)
1. Clone the repo (into the currect directory)
```sh
git clone https://github.com/bennettbDEV/BackpackBazaar.git .
```
2. (Optionally) Set up a [virtual environment](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/)
```sh
python -m venv venv
```
2a. Activate the virtual environment - for Windows:
```sh
.\venv\Scripts\activate
```
2b. Activate the virtual environment - for Linux/Mac:
```sh
source venv/bin/activate
```
3. Move to the backend directory 
```sh
cd backend
```
4. Install necessary packages
```sh
python -m pip install -r requirements.txt
```
5. Navigate back to the base directory
```sh
cd ..
```
6. Go to the frontend directory
```sh
cd frontend
```
7. Install necessary packages
```sh
npm install
```
8. Create an env file (Links our development servers together)
```sh
echo VITE_API_URL="http://localhost:8000/" > .env
```
**Run the servers** <br/>
9. Start the frontend
```sh
npm run dev
```
10. After splitting or creating a new terminal, navigate to BackpackBazaar/backend
```sh
cd ..
cd backend
```
11. Start the backend
```sh
python manage.py runserver
```
12. Done!
    Open a browser and enter "http://localhost:5173/" into the search bar to interact with the Marketplace
