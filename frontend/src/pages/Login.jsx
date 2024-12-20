import { useNavigate } from "react-router-dom"; 
import Form from "../components/Form";
import NavBar from "../components/Navbar.jsx";
import "./styles/Login.css";

function Login() {
    const navigate = useNavigate(); 

    return (
        <>
            <NavBar />
            <div className="login-container">
                <Form route="/api/token/" method="login" />
                <h2>New to ISU Marketplace?</h2>
                <button className="form-button" onClick={() => navigate("/register")}>
                    <b>Register</b>
                </button>
            </div>
        </>
    );
}

export default Login;