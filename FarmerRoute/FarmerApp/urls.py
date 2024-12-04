from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
			path("Signup.html", views.Signup, name="Signup"),
			path("SignupAction", views.SignupAction, name="SignupAction"),	    	
			path("UserLogin.html", views.UserLogin, name="UserLogin"),
			path("UserLoginAction", views.UserLoginAction, name="UserLoginAction"),
			path("AdminLogin.html", views.AdminLogin, name="AdminLogin"),
			path("AdminLoginAction", views.AdminLoginAction, name="AdminLoginAction"),
			path("UpdateProfile", views.UpdateProfile, name="UpdateProfile"),
			path("UpdateProfileAction", views.UpdateProfileAction, name="UpdateProfileAction"),
			path("SeekAdvice", views.SeekAdvice, name="SeekAdvice"),
			path("SeekAdviceAction", views.SeekAdviceAction, name="SeekAdviceAction"),
			path("CheckAdviceStatus", views.CheckAdviceStatus, name="CheckAdviceStatus"),
			path("ActivateProfile", views.ActivateProfile, name="ActivateProfile"),
			path("ActivateProfileAction", views.ActivateProfileAction, name="ActivateProfileAction"),
			path("ViewRequest", views.ViewRequest, name="ViewRequest"),
			path("ViewRequestAction", views.ViewRequestAction, name="ViewRequestAction"),
			path("AdvicePageAction", views.AdvicePageAction, name="AdvicePageAction"),
			path("AutoDisease.html", views.AutoDisease, name="AutoDisease"),
			path("AutoDiseaseAction", views.AutoDiseaseAction, name="AutoDiseaseAction"),
			path("Planning.html", views.Planning, name="Planning"),
			path("PlanningAction", views.PlanningAction, name="PlanningAction"),
]