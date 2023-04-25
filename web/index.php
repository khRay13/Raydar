<?php
	// Import request packages
	include("head.php");
?>

<style>
	iframe {
		padding: 0;
		width: 100%;
	}

	div {
		padding-left: 15px !important;
		padding-right: 15px !important;
	}
</style>

<div class="row" style="max-width: 100%;">
	<div class="col-2">
		<iframe id="ifm_Sidebox" name="ifm_Sidebox" src="Sidebox.php" frameborder="0"></iframe>
	</div>
	<div class="col-10">
		<iframe id="ifm_DualList" name="ifm_DualList" src="DualList.php" frameborder="0"></iframe>
	</div>
</div>

<script type="text/javascript">
	var frame1 = document.getElementById("ifm_Sidebox");
	frame1.onload = function(){
		frame1.style.height = frame1.contentWindow.document.body.scrollHeight + "px";
		frame1.style.width = frame1.contentWindow.document.body.scrollWidth + "px";
	}
	var frame2 = document.getElementById("ifm_DualList");
	frame2.onload = function(){frame2.style.height = frame2.contentWindow.document.body.scrollHeight + "px";}
</script>
