var express = require('express');
var app = express();
var mysql = require('mysql');
var session = require('express-session');
var path = require('path'); // Add this line to import the path module

// Session Middleware
app.use(session({
    secret: 'secretKey', // A secret key for encryption
    resave: false,
    saveUninitialized: true
}));

// Serve the login page at the root URL
app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname, 'login.html')); // Adjust the path as needed
});

app.use(express.json());

// MySQL Connection
var con = mysql.createConnection({
    host: "localhost",
    user: "rishabh",
    password: "abc123",
    database: "results"
});

con.connect(function(err) {
    if (err) throw err;
    console.log("Connected to DB.");
});

// Sign In Route (for new users)
app.post('/signin', function(req, res) {
    req.on('data', function(chunk) {
        let submittedAns = JSON.parse(chunk);
        console.log("DBG : " + chunk);

        // Check in database whether username already exists
        var sql = "SELECT * FROM login WHERE name='" + submittedAns.uname + "'";
        con.query(sql, function(err, result) {
            if (err) throw err;
            res.header("Access-Control-Allow-Origin", "*");

            if (result.length == 0) {
                // If username doesn't exist, insert new user into the database
                var currentDate = new Date().toISOString().slice(0, 19).replace("T", " "); // Get current date and time
                var sql = "INSERT INTO login (name, password, email, register_date) VALUES ('" + submittedAns.uname + "','" + submittedAns.psw + "','" + submittedAns.email + "','" + currentDate + "')";
                con.query(sql, function(err, result) {
                    if (err) throw err;
                    res.send({'result': 'Alright, you are signed in.'});
                });
            } else {
                res.send({'result': 'This username has already been used. Please use another username.'});
            }
        });
    });
});


// Login Route (for existing users)
app.post('/login', function(req, res) {
    req.on('data', function(chunk) {
        let submittedAns = JSON.parse(chunk);

        // Check if the username exists in the database
        var sql = "SELECT * FROM login WHERE name='" + submittedAns.uname + "'";
        con.query(sql, function(err, result) {
            if (err) throw err;
            res.header("Access-Control-Allow-Origin", "*");

            if (result.length == 0) {
                res.send({'result': 'Err: Login ' + submittedAns.uname + ' Doesn\'t Exist. Please Sign in.'});
            } else {
                // Check the password for the username
                var sql = "SELECT * FROM login WHERE password='" + submittedAns.psw + "'";
                con.query(sql, function(err, result) {
                    if (err) throw err;
                    if (result.length == 0) {
                        res.send({'result': 'Wrong Password! Please try again'});
                    } else {
                        // Store the username and email in the session
                        req.session.username = submittedAns.uname;
                        req.session.email = result[0].email; // Store email in session if needed
                        res.send({'result': 'OK, You are logged in'});
                    }
                });
            }
        });
    });
});


app.get('/post-history', function(req, res) {
res.header("Access-Control-Allow-Origin", "*");
    const username = req.session.username;  // Assuming you store the username in the session
    console.log(username);
    if (!username) {
        return res.json({ result: 'error', message: 'User not logged in' });
    }

    // Query the database for the user's post history
    const sql = "SELECT * FROM posts WHERE username='" + username + "'";
    con.query(sql, function(err, result) {
        if (err) {
            console.error(err);
            return res.json({ result: 'error', message: 'Error fetching post history' });
        }

        if (result.length == 0) {
            return res.json({ result: 'error', message:'No posts yet'});
        }
        else{

        // Format the posts data
        const posts = result.map(post => ({
            title: `Post on ${post.post_date}`,  // You can customize the title as needed
            content: post.post_content,
            date: post.post_date
        }));

        return res.json({ result: 'success', posts: posts });
        }
    });
});

app.get('/profile', function(req, res) {
    const username = req.session.username;  // Assuming the username is stored in the session
    if (!username) {
        return res.json({ result: 'error', message: 'User not logged in' });
    }

    // Query the database for the user's profile details
    const sql = "SELECT name, email, register_date FROM login WHERE name ='" + username + "'";;
    con.query(sql, function(err, result) {
        if (err) {
            console.error(err);
            return res.json({ result: 'error', message: 'Error fetching profile data' });
        }

        if (result.length == 0) {
            return res.json({ result: 'error', message: 'Profile not found' });
        }

        // Send profile data back to the client
        return res.json({
            result: 'success',
            profile: {
                username: result[0].name,
                email: result[0].email,
                register_date: result[0].register_date
            }
        });
    });
});

app.post('/submit-complaint', function(req, res) {
    const { username, complaint } = req.body;

    // Log the incoming data for debugging
    console.log("Received complaint data:", req.body);

    // Check if complaint data exists
    if (!username || !complaint) {
        return res.json({ result: 'error', message: 'Username and complaint content are required' });
    }

    // Use prepared statement to avoid SQL injection
    const sql = "INSERT INTO complaints (username, complaint_content, date_submitted) VALUES (?, ?, NOW())";
    con.query(sql, [username, complaint], function(err, result) {
        if (err) {
            console.error("Database error:", err);
            return res.json({ result: 'error', message: 'Error submitting complaint' });
        }
        console.log("Complaint inserted successfully!");
        return res.json({ result: 'success', message: 'Complaint submitted successfully' });
    });
});

app.use(express.static('public'));
app.use('/css', express.static(__dirname + '/css'));
app.use('/js', express.static(__dirname + '/js'));
app.use('/images', express.static(__dirname + '/images'));
app.use('/', express.static(__dirname + ''));

var server = app.listen(3001, function() {
    var port = server.address().port;
    console.log("Server started at http://localhost:%s", port);
});

