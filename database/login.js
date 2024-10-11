import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

document.getElementById('login-btn').addEventListener('click', async () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    console.log('Login button clicked');
    console.log('Username:', username);
    console.log('Password:', password);

    if (username && password) {
        try {
            // Open the SQLite database
            const db = await open({
                filename: '/login.db',
                driver: sqlite3.Database
            });

            // Query to check username and password
            const query = `SELECT * FROM login WHERE user = ? AND password = ?`;
            const user = await db.get(query, [username, password]);

            if (user) {
                console.log('Username and password match');
                const token = btoa(username + ':' + password);
                const expires = new Date();
                expires.setTime(expires.getTime() + (24 * 60 * 60 * 1000)); // 1 day

                // Set token as a cookie
                document.cookie = `token=${token}; expires=${expires.toUTCString()}; path=/;`;
                console.log('Token set in cookies:', document.cookie);

                // Update token in the database
                await db.run(`UPDATE login SET token = ? WHERE id = ?`, [token, user.id]);
                console.log('Token updated in database');
                
                document.getElementById('notification').textContent = "Login successful!";
                document.getElementById('notification').style.color = "green";

                // Redirect to dashboard
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 2000); // 2 seconds delay
            } else {
                console.log('Username or password does not match');
                document.getElementById('notification').textContent = "Login failed! Invalid username or password.";
                document.getElementById('notification').style.color = "red";
            }
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('notification').textContent = "An error occurred. Please try again.";
        }
    } else {
        console.log('Username or password missing');
        document.getElementById('notification').textContent = "Please enter both username and password.";
    }
});
