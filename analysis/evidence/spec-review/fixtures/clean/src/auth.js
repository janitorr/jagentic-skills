export function requireUser(request) {
  const userId = request.session?.userId;
  if (!userId) {
    const error = new Error("unauthorized");
    error.status = 401;
    throw error;
  }
  return userId;
}
