let lastError: Error | null = null;

export function consumeLastCapturedError() {
  const err = lastError;
  lastError = null;
  return err;
}

export function captureError(err: Error) {
  lastError = err;
}
