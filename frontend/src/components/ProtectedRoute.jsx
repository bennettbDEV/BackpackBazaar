import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../contexts/AuthProvider";

function ProtectedRoute({ children }) {
    const { isAuthorized } = useContext(AuthContext);

    if (!isAuthorized) {
        return <Navigate to="/login" />;
    }

    return children;
}

export default ProtectedRoute;
