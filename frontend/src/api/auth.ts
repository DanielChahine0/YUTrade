// Assigned to: Mai Komar
// Phase: 1 (F1.8)
//
// TODO: Auth API functions.
//
// import client from "./client"
// import { RegisterRequest, LoginRequest, VerifyRequest, TokenResponse } from "../types"
//
// register(data: RegisterRequest): Promise
//   - POST /auth/register with { email, password, name }
//   - Return response.data
//
// verify(data: VerifyRequest): Promise
//   - POST /auth/verify with { email, code }
//   - Return response.data
//
// login(data: LoginRequest): Promise<TokenResponse>
//   - POST /auth/login with { email, password }
//   - Return response.data (contains access_token, token_type, user)

import client from "./client"
import { RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, UpdateProfileRequest, ChangePasswordRequest, DeleteAccountRequest, User } from "../types"

export const register = (data: RegisterRequest) => {
    return client.post("/auth/register", data).then((response) => response.data)
}

export const login = (data: LoginRequest) => {
    return client.post("/auth/login", data).then((response) => response.data)
}

export const forgotPassword = (data: ForgotPasswordRequest) => {
    return client.post("/auth/forgot-password", data).then((response) => response.data)
}

export const resetPassword = (data: ResetPasswordRequest) => {
    return client.post("/auth/reset-password", data).then((response) => response.data)
}

export const getMe = (): Promise<User> => {
    return client.get("/auth/me").then((response) => response.data)
}

export const updateProfile = (data: UpdateProfileRequest): Promise<User> => {
    return client.patch("/auth/me", data).then((response) => response.data)
}

export const changePassword = (data: ChangePasswordRequest) => {
    return client.post("/auth/change-password", data).then((response) => response.data)
}

export const deleteAccount = (data: DeleteAccountRequest) => {
    return client.post("/auth/delete-account", data).then((response) => response.data)
}
