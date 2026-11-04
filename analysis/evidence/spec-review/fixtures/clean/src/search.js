export async function searchTasks(db, userId, term) {
  return db.tasks.findMany({
    where: { userId, title: { contains: term } },
  });
}
