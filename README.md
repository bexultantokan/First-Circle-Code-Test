Hello, this is my code test for the First Circle. 

Here, I created a program imitating the bank system. It's written in Python and utilizes the terminal-like interface. 
In order to launch the program, you may need to install Firebase Admin SDK.
* The program handles all the required functions (account creation and management, depositing, withdrawal, transfer, checking the account balance).
* I utilized the Firebase Database so you can launch this program on any device and the data will be consistent. 
* Also, I utilized the Firebase's Transaction feature, which enables me to lock a certain Firebase document and make operations on it (atomic operations). It ensures that any possible concurrent programs will not interfere with each other and depositing and withdrawal will be correct. 
* I also hashed all the entered passwords so if anyone accesses the database, he/her still won't be able to access the accounts. 
* Whenever I required the user input, I made sure to validate it. When checking if a certain login exists, I optimized the process by querying only the document name, avoiding the need to download the entire document.
* I tried to make functions as reusable as possible. 

If you have any questions, please don't hesitate to contact me. Thanks!


UPD: The Firebase credentials were banned by google for being exposed on Github. Please ask Mr. Justin Hart to forward the new ones, I've sent them to him. Sorry for the inconvenience caused.
