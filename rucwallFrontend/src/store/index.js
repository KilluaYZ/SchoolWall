import {createStore} from "vuex";
function parseInitState(key){
    return sessionStorage.getItem(key) != null? sessionStorage.getItem(key) : "";
}
const store = createStore({
    state:{
        token: parseInitState("token"),
        username: ''
    },
    mutations:{
        saveToken(state, token){
            state.token = token;
            sessionStorage.setItem("token", token);
        },
        saveUsername(state, username){
            state.username = username;
        },
        clearSystemInfo(state){
            state.token = "";
            state.username = "";
            sessionStorage.removeItem("token");
        }
    },

    actions:{
        saveToken(context, token){
            context.commit("saveToken", token);
        },
        saveUsername(context, username){
            context.commit("saveUsername", username);
        },
        clearSystemInfo(context){
            context.commit("clearSystemInfo");
        }
    },
    getters:{
        token(state){
            return state.token;
        },
        username(state){
            return state.username;
        }
    }
});

export default store;