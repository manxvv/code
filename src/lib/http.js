import axios from "axios";
import Urls from "../config/urls";
import { store } from "@/app/store";
import { useNavigate } from "react-router-dom";
import { login, logout, setAuthToke } from "@/features/auth/authSlice";


console.log(window.location.host,"dsadasdas")

const http = axios.create({
  baseURL: Urls.baseURL,
  withCredentials: true
});

http.interceptors.request.use(
  (config) => {
    const token = store.getState().auth.access_token;

    console.log(store.getState().auth,"store.getState()store.getState()")
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    if (config.data instanceof FormData) {
      config.headers["Content-Type"] = "multipart/form-data";
    } else {
      config.headers["Content-Type"] = "application/json";
    }
    return config;
  },
  (error) => Promise.reject(error)
);

http.interceptors.response.use(
  (response) => {

    console.log(response, "response.headersresponse.headers")
    let newToken = response.headers["authorization"];

    if (response && response.config && response.config.headers) {
      newToken = response.config.headers.Authorization
    }


    console.log(newToken, "newTokennewTokennewTokennewToken")
    if (newToken) {
      console.log("authDataauthDataauthData", localStorage.getItem("authData"))


      let oldLocalStorage = JSON.parse(localStorage.getItem("authData"))

      console.log(oldLocalStorage, "oldLocalStorageoldLocalStorage")

      const tokenOnly = newToken.split(" ")[1];

      localStorage.setItem("authDataasas", JSON.stringify({
        user: oldLocalStorage.user,
        "access_token": tokenOnly
      }));
      console.log(tokenOnly, oldLocalStorage.user, "tokenOnlytokenOnly")

      store.dispatch(login({ user: oldLocalStorage.user, "access_token": tokenOnly }));
      console.log(tokenOnly, oldLocalStorage.user, "tokenOnlytokenOnly")
      // store.dispatch(setAuthToke(tokenOnly));
    }
    return response;
  },
  (error) => {
    console.log(error.response, status, "errorerrorerrorerrorerrorerror")
    if (error.response && error.response.status === 401) {
      store.dispatch(logout());
      window.location.replace("/auth/login");
    }
    return Promise.reject(error);
  }
);

export default http;
