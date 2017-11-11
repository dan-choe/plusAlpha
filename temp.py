from firebase import firebase

fb = firebase.FirebaseApplication('https://plusalpha-77c9d.firebaseio.com', None)
result = fb.get('/users', None)
print(result)

# fb = firebase.FirebaseApplication('https://plusalpha-77c9d.firebaseio.com', None)
# r = fb.post('/users', 'new user', {'print': 'pretty'}, {'X_FANCY_HEADER': 'VERY FANCY'})
r = fb.post('/users', data={'key1':"haha","whatever":"data"})
print(r)


# <script src="https://www.gstatic.com/firebasejs/4.6.2/firebase.js"></script>
# <script>
#   // Initialize Firebase
#   var config = {
#     apiKey: "AIzaSyCBKvvMF5c-aUQVdZFAV8GBenslVjaxHUQ",
#     authDomain: "plusalpha-77c9d.firebaseapp.com",
#     databaseURL: "https://plusalpha-77c9d.firebaseio.com",
#     projectId: "plusalpha-77c9d",
#     storageBucket: "plusalpha-77c9d.appspot.com",
#     messagingSenderId: "824382801036"
#   };
#   firebase.initializeApp(config);
# </script>