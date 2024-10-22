{
	pkgs ? import <nixpkgs> { },
	python3Packages ? pkgs.python3Packages,
}:

let
	inherit (pkgs) lib;
	base = python3Packages.callPackage ./package.nix { };

	foldToList = list: f: lib.foldl' f [ ] list;
	pipeNullable = lib.foldl' (value: f: lib.mapNullable f value);
	maybeGetAttrFrom = attrset: name: attrset."${name}" or null;
	append = appendage: base: base + appendage;

in base.overrideAttrs (prev: {
	passthru = lib.recursiveUpdate (prev.passthru or { }) {
		byPythonVersion = let
			pyInterpreters = lib.attrValues pkgs.pythonInterpreters;
			listOfAttrs = foldToList pyInterpreters (acc: python: let
				attr = python.pythonAttr or null;
				isPy3 = python.isPy3 or false;
				scope = pipeNullable attr [
					(append "Packages")
					(maybeGetAttrFrom pkgs)
				];
				isValid = scope != null && isPy3;
			in acc ++ lib.optional isValid {
				name = scope.python.pythonAttr;
				value = scope.callPackage ./package.nix { };
			});
		in lib.listToAttrs listOfAttrs;
	};
})
