function validateGeneratedPost(post) {
  if (!post || typeof post !== 'object') {
    throw new Error('Generated payload is not an object.');
  }

  const required = ['title', 'content', 'meta_desc', 'seo_title'];
  for (const key of required) {
    if (!post[key] || typeof post[key] !== 'string') {
      throw new Error(`Generated payload missing required string field: ${key}`);
    }
  }

  if (post.content.length < 100) {
    throw new Error('Generated content is too short for safe publish policy.');
  }

  if (post.seo_title.length > 60) {
    post.seo_title = post.seo_title.slice(0, 60);
  }

  if (post.meta_desc.length > 160) {
    post.meta_desc = post.meta_desc.slice(0, 160);
  }

  if (!Array.isArray(post.tags)) {
    post.tags = [];
  }

  return post;
}

function validateScheduleDate(scheduleIso) {
  if (!scheduleIso || typeof scheduleIso !== 'string') {
    throw new Error('Schedule date is required.');
  }

  const when = new Date(scheduleIso);
  if (Number.isNaN(when.getTime())) {
    throw new Error('Schedule date must be a valid ISO timestamp.');
  }

  if (when.getTime() <= Date.now()) {
    throw new Error('Schedule date must be in the future.');
  }

  return when.toISOString();
}

module.exports = {
  validateGeneratedPost,
  validateScheduleDate
};
