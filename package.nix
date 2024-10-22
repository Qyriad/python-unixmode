# python3Packages.callPackage
{
	lib,
	stdenvNoCC,
	python,
	setuptools,
	pytestCheckHook,
	wheel,
	pypaBuildHook,
	pypaInstallHook,
	pythonCatchConflictsHook,
	pythonRuntimeDepsCheckHook,
	pythonNamespacesHook,
	pythonOutputDistHook,
	pythonImportsCheckHook,
	ensureNewerSourcesForZipFilesHook,
	pythonRemoveBinBytecodeHook,
	wrapPython,
}: let
	stdenv = stdenvNoCC;
	# FIXME: should this be python.stdenv?
	inherit (stdenv) hostPlatform buildPlatform;
in stdenv.mkDerivation (self: {
	pname = "${python.name}-richmode";
	version = "0.0.1";

	strictDeps = true;
	__structuredAttrs = true;

	doCheck = true;
	doInstallCheck = true;


	src = lib.fileset.toSource {
		root = ./.;
		fileset = lib.fileset.unions [
			./src
			./pyproject.toml
		];
	};

	outputs = [ "out" "dist" ];

	nativeBuildInputs = [
		pypaBuildHook
		pypaInstallHook
		pythonRuntimeDepsCheckHook
		pythonOutputDistHook
		ensureNewerSourcesForZipFilesHook
		pythonRemoveBinBytecodeHook
		wrapPython
		setuptools
	] ++ lib.optionals (buildPlatform.canExecute hostPlatform) [
		pythonCatchConflictsHook
	] ++ lib.optionals (python.pythonAtLeast "3.3") [
		pythonNamespacesHook
	];

	nativeCheckInputs = [
		pythonImportsCheckHook
	];

	nativeInstallCheckInputs = [
		pythonImportsCheckHook
		#pytestCheckHook
	];

	postFixup = ''
		echo "wrapping Python programs in postFixup..."
		wrapPythonPrograms
		echo "done wrapping Python programs in postFixup"
	'';

	passthru = {
		mkDevShell = {
			mkShellNoCC,
			pyright,
			pylint,
			uv,
		}: mkShellNoCC {
			inputsFrom = [ self.finalPackage ];
			packages = [
				pyright
				pylint
				uv
			];
		};
	};

	meta = {
		isBuildPythonPackage = python.meta.platforms;
	};
})
