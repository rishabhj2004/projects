var express = require('express');
var app = express();
var mysql = require('mysql');
var session = require('express-session');
var path = require('path'); // Add this line to import the path module
const csv = require('csv-parser');
const fs = require('fs');
const bodyParser = require('body-parser');
const multer = require('multer');

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
app.use(bodyParser.json());

// Configure file storage
const storage = multer.diskStorage({
    destination: './uploads',
    filename: (req, file, cb) => {
        cb(null, Date.now() + path.extname(file.originalname));
    }
});
const upload = multer({ storage });

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
                        var sql = "SELECT * FROM admin WHERE username='" + submittedAns.uname + "'";
                        con.query(sql, function(err, result) {
                    	    if (err) throw err;
                            if(result.length == 0){
                                res.send({'result': 'OK, You are logged in'});
                            }
                            else{
                                res.send({'result':'Admin logged in'});
                            }
                        });
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
            date: post.post_date,
            status: post.status
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

let pincodeData = [];
fs.createReadStream('Pincode.csv')
  .pipe(csv())
  .on('data', (row) => {
    pincodeData.push(row);
  })
  .on('end', () => {
    console.log('CSV file successfully processed');
  });

app.post('/pincode-search', (req, res) => {
  try {
    const { state, district, officeName } = req.body;

    const results = pincodeData.filter(item => {
      const matchState = state ? item.StateName && item.StateName.toLowerCase() === state.toLowerCase() : true;
      const matchDistrict = district ? item.District && item.District.toLowerCase() === district.toLowerCase() : true;
      const matchOfficeName = officeName ? item['Office Name'] && item['Office Name'].toLowerCase() === officeName.toLowerCase() : true;

      return matchState && matchDistrict && matchOfficeName;
    });

    if (results.length === 0) {
      console.log("No results found for the given parameters.");
    } else {
      console.log("Results found:", results);
    }

    return res.json({ result: 'success', data: results });
  } catch (error) {
    console.error("Error in /pincode-search route:", error);
    res.status(500).json({ result: 'error', message: 'Server error occurred' });
  }
});

app.post('/submit-service', upload.single('file'), (req, res) => {
    const { address } = req.body;
    const username = req.session.username; // Assuming the username is stored in session
    const filePath = req.file ? req.file.path : null;

    // Insert the service request into the `posts` table
    const query = `INSERT INTO posts (username, post_content, address, status) VALUES (?, ?, ?, 'processing')`;
    con.query(query, [username, filePath, address], (err, result) => {
        if (err) {
            console.error(err);
            res.status(500).json({ message: 'Error saving service request' });
        } else {
            res.json({ message: 'Service request submitted successfully' });
        }
    });
});

app.get('/complaint-history', function(req, res) {
res.header("Access-Control-Allow-Origin", "*");
    const username = req.session.username;  // Assuming you store the username in the session
    console.log(username);
    if (!username) {
        return res.json({ result: 'error', message: 'User not logged in' });
    }

    // Query the database for the user's post history
    const sql = "SELECT * FROM complaints";
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
            title: `Post on ${post.date_submitted}`,  // You can customize the title as needed
            uname: post.username,
            content: post.complaint_content,
        }));

        return res.json({ result: 'success', posts: posts });
        }
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

