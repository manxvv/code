import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  user: null,
  access_token: null,
  refresh_token: null,
  isAuthenticated: false,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    login: (state, action) => {
      const { user, access_token, refresh_token } = action.payload;
      state.user = user;
      state.access_token = access_token;
      state.refresh_token = refresh_token;
      state.isAuthenticated = true;
    },
    logout: (state) => {
      state.user = null;
      state.access_token = null;
      state.refresh_token = null;
      state.isAuthenticated = false;
      localStorage.removeItem('authData');
    },

    initializeAuth: (state, action) => {
      const { user, access_token, refresh_token } = action.payload;
      state.user = user;
      state.access_token = access_token;
      state.refresh_token = refresh_token;
      state.isAuthenticated = true;
    },


    setAuthToke:(state, action) => {
      state.access_token = action.payload
    }


  },
});

export const { login, logout,setAuthToke, initializeAuth } = authSlice.actions;
export default authSlice.reducer;