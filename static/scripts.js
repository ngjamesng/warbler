$(function() {
	$(".follow").on("click", ".btn", async function(evt) {
		await handleFollow(evt);
	});

	$(".follow-other-user-page").on("click", ".btn", async function(evt) {
		await handleFollowOther(evt);
	});


	$(".like-form").on("click", ".like", async function(evt) {
		await handleLikes(evt);
	});
});

async function handleFollow(evt) {
	evt.preventDefault();
	let form = evt.target.parentElement;
	const followUserId = form.dataset.userId;
	const response = await axios.post(`/users/handlefollow/${followUserId}`);
  form.innerHTML = response.data.html;
  $("#following-count").empty().append(response.data.follow_count)
}

async function handleFollowOther(evt) {
	evt.preventDefault();
	let form = evt.target.parentElement;
	const followUserId = form.dataset.userId;
	const response = await axios.post(`/users/handlefollow/${followUserId}`);
	form.innerHTML = response.data.html;
	console.log("FOLLOWER COUNT:!!!!!", response.data)
  $("#follower-count").empty().append(response.data.follower_count)
}

async function handleLikes(evt) {
	evt.preventDefault();
  let $star = $(evt.target.closest("i"));

  const messageId =  $(evt.target.closest("form")).data().messageId;
  const response = await axios.post(`/messages/${messageId}/handle-like`);
	if (response) {
    $star.toggleClass("far fas");
    $("#user-likes").empty().append(response.data.count)
	}
}
