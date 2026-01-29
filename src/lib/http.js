import axios from "axios";
import Urls from "../config/urls";
import { store } from "@/app/store";
import { useNavigate } from "react-router-dom";
import { login, logout, setAuthToke } from "@/features/auth/authSlice";
import Swal from "sweetalert2";




// console.log(window.location.host,"dsadasdas")


let all_urls={
  "vedang.dataplus.live":"https://api.vedang.dataplus.live",
  "dataplus.mpulsenet.com":"https://api.mpulsenet.dataplus.live",
  // "localhost:5174":"https://5352aaad8058.ngrok-free.app",
  "localhost:5175":"http://localhost:5000"
}

export const final_url = `https://api.mpulsenet.dataplus.live`
// console.log(window.location.host,"use1324354657");


console.log("Current host:", window.location.host);
console.log("Using base URL:", final_url);
const http = axios.create({
  baseURL: all_urls[window.location.host],
baseURL:`${Urls.baseURL}`,
  withCredentials: true
});

http.interceptors.request.use(
  (config) => {
    const token = store.getState().auth.access_token;
    // console.log(store.getState().auth,"store.getState()store.getState()")
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    if (config.data instanceof FormData) {
      console.log(config.data)
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

    // console.log(response, "response.headersresponse.headers")
    let newToken = response.headers["authorization"];

    if (response && response.config && response.config.headers) {
      newToken = response.config.headers.Authorization
    }


    // console.log(newToken, "newTokennewTokennewTokennewToken")
    if (newToken) {
      // console.log("authDataauthDataauthData", localStorage.getItem("authData"))


      let oldLocalStorage = JSON.parse(localStorage.getItem("authData"))

      // console.log(oldLocalStorage, "oldLocalStorageoldLocalStorage")

      const tokenOnly = newToken.split(" ")[1];

      localStorage.setItem("authDataasas", JSON.stringify({
        user: oldLocalStorage.user,
        "access_token": tokenOnly
      }));
      // console.log(tokenOnly, oldLocalStorage.user, "tokenOnlytokenOnly")

      store.dispatch(login({ user: oldLocalStorage.user, "access_token": tokenOnly }));
      // console.log(tokenOnly, oldLocalStorage.user, "tokenOnlytokenOnly")
      // store.dispatch(setAuthToke(tokenOnly));
    }
    return response;
  },
  async (error) => {
    // console.log(error.response, status, "errorerrorerrorerrorerrorerror")
    if (error.response && error.response.status === 401) {
      store.dispatch(logout());
      window.location.replace("/auth/login");
    }
    if (error.response) {
      const { data, headers } = error.response;
      const contentType = headers?.["content-type"] || "";

      
      if (
        data instanceof Blob &&
        contentType.includes("application/json")
      ) {
        const text = await data.text();
        const json = JSON.parse(text);
        error.response.data = json;
      }

      
      if (
        error.response.data?.message &&
        !error.config?.skipToast
      ) {
        Swal.fire({
          toast: true,
          position: "top-end",
          icon: "warning",
          title: error.response.data.message,
          showConfirmButton: false,
          timer: 4000,
          timerProgressBar: true,
        });
      }
    }
    return Promise.reject(error);
  }
);

export default http;
