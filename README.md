# BroDeen: Quran & Hadith Explorer

## Overview

BroDeen is a comprehensive web application designed to help users explore the Quran and authentic Hadith collections with ease. Built as my CS50x 2025 final project, this platform integrates modern web technologies and external APIs to deliver a seamless and interactive Islamic learning experience.

## Features

- **Quran Explorer:**  
  Browse all 114 surahs of the Quran, view detailed information, and read translations. Each surah page displays the surah’s name, number, revelation type, and ayah count, with ayah-by-ayah navigation.

- **Search Functionality:**  
  Instantly search the entire Quran by keyword, with results showing the relevant ayah, translation, surah name, and ayah number. Pagination ensures efficient browsing of large result sets.

- **Hadith Collections:**  
  Access the full texts of Sahih al-Bukhari, Sahih Muslim, and Jami At-Tirmidhi. The application extracts and displays the contents of PDF files for each collection, making them readable and accessible directly in the browser.

- **Responsive Design:**  
  The site is fully responsive and user-friendly, thanks to a modern HTML template that ensures a consistent experience across devices.

- **API Integration:**  
  Quranic data is fetched in real-time from the [AlQuran Cloud API](https://alquran.cloud/api), ensuring up-to-date and accurate information.

- **Error Handling:**  
  The app gracefully handles missing data, API errors, and PDF extraction issues, providing clear feedback to users.

## Technologies Used

- **Python & Flask:** Backend framework for routing, API integration, and PDF processing.
- **HTML5, CSS3:** Frontend structure and styling, based on a professional HTML template.
- **Jinja2:** For dynamic content rendering.
- **PyPDF2:** To extract and display text from Hadith PDF files.
- **JavaScript:** For interactive elements and enhanced user experience.
- **REST APIs:** For Quranic data retrieval.

## What I Learned

Working on BroDeen was a transformative experience. I deepened my understanding of:

- **Web Development:**  
  Building a full-stack web application from scratch, structuring Flask routes, and managing templates.

- **API Consumption:**  
  Integrating third-party APIs, handling JSON data, and managing asynchronous data fetching.

- **PDF Processing:**  
  Extracting and rendering text from complex PDF files, and handling edge cases such as missing or malformed documents.

- **User Experience:**  
  Designing intuitive navigation, implementing search and pagination, and ensuring accessibility.

- **Debugging & Error Handling:**  
  Diagnosing issues with API requests, PDF extraction, and template rendering, and providing user-friendly error messages.

- **Project Management:**  
  Planning, organizing, and iteratively improving a substantial codebase.

## How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dedguyyy/Project
   cd brodeen

2.Install dependencies:
    pip install -r requirements.txt

3.Add PDF files:
    Place bukhari.pdf, muslim.pdf, and tirmidhi.pdf in the static/pdfs/ directory.

4.Run the app:
    python app.py

5.Open your browser:
Visit http://127.0.0.1:5000 to explore the site.

Acknowledgments
CS50x 2025 for the opportunity and guidance.
AlQuran Cloud API for providing Quranic data.
The creators of the HTML template that gave the site its modern look and feel.

Overview
BroDeen is more than just a project—it's a reflection of my journey through CS50x, combining technical growth with a deeper appreciation for Islamic knowledge. Thank you for visiting! ```
