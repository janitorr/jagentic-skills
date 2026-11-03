export async function searchTasks(userId: string, term: string) {
  return db.tasks.findMany({
    where: { userId, title: { contains: term } },
  });
}
