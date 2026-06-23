/**
 * @module types/user
 * @description Type definitions for user entities and authentication-related
 * request/response payloads.
 */

/** Represents a user returned by the API. */
export interface User {
  /** Unique identifier (UUID). */
  id: string
  /** Unique username. */
  username: string
  /** Unique email address. */
  email: string
  /** Display name chosen by the user, or `null`. */
  display_name: string | null
  /** URL of the user's avatar image, or `null`. */
  avatar_url: string | null
  /** ISO-8601 timestamp when the account was created. */
  created_at: string
}

/** Payload for the login endpoint. */
export interface LoginRequest {
  /** User's email address. */
  email: string
  /** User's password. */
  password: string
}

/** Payload for the registration endpoint. */
export interface RegisterRequest {
  /** Desired username. */
  username: string
  /** User's email address. */
  email: string
  /** User's password. */
  password: string
  /** Optional display name. */
  display_name?: string
}

/** Response from login/register endpoints containing JWT tokens and the user. */
export interface TokenResponse {
  /** JWT access token for API authentication. */
  access_token: string
  /** JWT refresh token used to obtain a new access token. */
  refresh_token: string
  /** Token type (always `"bearer"`). */
  token_type: string
  /** The authenticated user. */
  user: User
}

/** Payload for updating the current user's profile. All fields are optional. */
export interface UserUpdateRequest {
  /** New display name. */
  display_name?: string
  /** New avatar URL. */
  avatar_url?: string
}
