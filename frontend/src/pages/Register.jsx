import React, { useState } from "react";
import NavBar from "../components/Navbar.jsx";
import RegistrationForm from "../components/RegistrationForm";
import "./styles/Register.css";

function Register() {
    return (
        <>
            <NavBar />
            <div className="registration-container">
                <RegistrationForm route="/api/users/"/>
            </div>
            
        </>
    );
}

export default Register;
