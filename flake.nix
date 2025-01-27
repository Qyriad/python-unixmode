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

		python-unixmode = import ./default.nix { inherit pkgs; };

		# default.nix exposes python-unixmode evaluated for multiple `pythonXPackages` sets,
		# so let's translate that to additional flake output attributes.
		extraVersions = lib.mapAttrs' (pyName: value: {
			name = "${pyName}-unixmode";
			inherit value;
		}) python-unixmode.byPythonVersion;

		packages = extraVersions // {
			default = python-unixmode;
			inherit python-unixmode;
			python3-unixmode = python-unixmode;
		};

		devShells = lib.mapAttrs (name: value: pkgs.callPackage value.mkDevShell { }) packages;
	in {
		inherit packages devShells;
	});
}
