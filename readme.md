# This is a project to use Watson Visual recognition and implement it in a Django website

For this project, I have created a free IBM Cloud log in and am using the Lite Free plan. I created a Project in IBM Watson and added the ImageRecongition Service to it. I used Custom Image classification to identify wrinkles in a specific kind of cloth. The custom object classified is "Wrinkle"

The Django website use the IBM Watson API to analyze and detect the presence of objects in the image. Since the projects collection id is trained to classify "Wrinkles", any objects classified would be a Wrinkle. This shows up as a red box along with the confidence percentage in the resulting page.
