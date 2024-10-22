{
	inputs = {
		nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
		flake-utils.url = "github:numtide/flake-utils";
	};

	outputs = {
		self,
		nixpkgs,
		flake-utils,
	}: flake-utils.lib.eachDefaultSystem (system: let
		pkgs = import nixpkgs { inherit system; };
		inherit (pkgs) lib;

		python-richmode = import ./default.nix { inherit pkgs; };

		# default.nix exposes python-richmode evaluated for multiple `pythonXPackages` sets,
		# so let's ranslate that to additional flake output attributes.
		extraVersions = lib.mapAttrs' (pyName: value: {
			name = "${pyName}-richmode";
			inherit value;
		}) python-richmode.byPythonVersion;

		packages = extraVersions // {
			default = python-richmode;
			inherit python-richmode;
			python3-richmode = python-richmode;
		};

		devShells = lib.mapAttrs (name: value: pkgs.callPackage value.mkDevShell { }) packages;
	in {
		inherit packages devShells;
	});
}
