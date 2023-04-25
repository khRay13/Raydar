<?php
include("head.php");

/**
	 * verify column_tracked
	 */
class verify_tracked
{
	public $conn;
	function __construct()
	{
		$this->Conn();
	}

	// SQL Connection
	function Conn(){
		try {
			$this->conn = new PDO("sqlsrv:Server=.\SQLEXPRESS;Database=Shipdt", NULL, NULL);
			$this->conn->exec("SET CHARACTER SET utf8");
			$this->conn->setAttribute( PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION );
		} catch(Exception $e) {
			print_r("<h3>Func_Conn Something Wrong !!</h3></br>");
			die(print_r("<h3>".$e->getMessage()."</h3>"));
		}
	}

	function query_data($VSLN, $PORT){
		try {
			$pre = $this->conn->prepare("SELECT MMSI, VSLNM, FVTP, IBT, RecTime, Tracked FROM IBTDB WHERE VSLNM = '".$VSLN."' AND PortNo = '".$PORT."' ORDER BY Tracked, RecTime DESC");
			$pre->execute();
			$rows = $pre->fetchAll();
			if (count($rows)) {
				return [true, $rows];
			} else {
				return [false, ""];
			}
		} catch (Exception $e) {
			print_r("<h3>Func_query_data Something Wrong !!</h3></br>");
			die(print_r("<h3>".$e->getMessage()."</h3>"));
		}
	}

	function upd_data(){
		try {
			$PORT = $_COOKIE["PORT"];
			$VSLN = $_COOKIE["VSLN"];
			$sql = "UPDATE IBTDB SET Tracked='1' WHERE PortNo='{$PORT}' AND VSLNM='{$VSLN}' AND Tracked='0'";
			$pre = $this->conn->prepare($sql);
			$rst = $pre->execute();
			return $rst;
		} catch (Exception $e) {
			print_r("<h3>Func_upd_data Something Wrong !!</h3></br>");
			die(print_r("<h3>".$e->getMessage()."</h3>"));
		}
	}
}

?>
<head>
	<style>
		.center {
			text-align: center;
			vertical-align: middle;
		}
	</style>
</head>

<body onload="resize();">
	<button id="btn_vfy" name="btn_vfy" class="btn btn-warning center" style="margin-bottom: 1em;" value="Verify">Verify</button>
	<table class="table table-bordered table-hover table-sm">
		<thead>
			<tr>
				<th scope="col" class="center">MMSI</th>
				<th scope="col" class="center">Vessel Name</th>
				<th scope="col" class="center">Vessel Type</th>
				<th scope="col" class="center">IBT</th>
				<th scope="col" class="center">RecTime</th>
				<th scope="col" class="center">Tracked</th>
			</tr>
		</thead>
		<tbody id="tbd">
			<?php
				$vfy = new verify_tracked();
				[$stat, $data] = $vfy->query_data($_COOKIE["VSLN"], $_COOKIE["PORT"]);

				if ($stat) {
					foreach ($data as $key => $val) {
						[$MMSI, $VSLN, $FVTP, $IBT, $RecTime, $Tracked] = $val;

						$s = "<tr>";
						$s.= "<td class='center'>{$MMSI}</td>";
						$s.= "<td class='center'>{$VSLN}</td>";
						$s.= "<td class='center'>{$FVTP}</td>";
						$s.= "<td class='center'>{$IBT}</td>";
						$s.= "<td class='center'>{$RecTime}</td>";
						$s.= "<td class='center'>{$Tracked}</td>";
						$s.= "</tr>";
						echo $s;
					}
				} else {
					echo "<tr><td colspan='6' class='center'><h5>Vessel: {$_COOKIE["VSLN"]}, Port: {$_COOKIE["PORT"]}, Not Found</h5></td></tr>";
				}
			?>
		</tbody>
	</table>
</body>

<script type="text/javascript">
	function resize(){
		parent.document.getElementById("frm_data").height = document.body.scrollHeight;
	}

	$("#btn_vfy").click(function() {
		$.cookie("FLAG", "1");
		location.reload();
	});
</script>

<?php

if (isset($_COOKIE["FLAG"]) && $_COOKIE["FLAG"]=="1") {
	// FLAG歸零
	echo "<script>$.cookie('FLAG', '0');</script>";

	$vfy->upd_data();
	echo "<script>location.reload();</script>";
}

?>