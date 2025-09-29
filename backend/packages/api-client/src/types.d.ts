/**
 * Type augmentations for Axios to support custom properties
 */

declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: {
      startTime: number;
    };
    _retry?: boolean;
    _retryCount?: number;
    retries?: number;
  }
}