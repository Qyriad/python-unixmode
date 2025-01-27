# python3Packages.callPackage
{
	lib,
	stdenvNoCC,
	python,
	setuptools,
	wheel,
	pytestCheckHook,
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
	pname = "${python.name}-unixmode";
	version = "0.0.1";

	strictDeps = true;
	__structuredAttrs = true;

	doCheck = true;
	doInstallCheck = true;

	src = lib.fileset.toSource {
		root = ./.;
		fileset = lib.fileset.unions [
			./pyproject.toml
			./src
			./tests
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

	nativeInstallCheckInputs = [
		pythonImportsCheckHook
		pytestCheckHook
	];

	postFixup = ''
		echo "wrapping Python programs in postFixup..."
		wrapPythonPrograms
		echo "done wrapping Python programs in postFixup"
	'';

	passthru = {
		mkDevShell = {
			mkShellNoCC,
			pylint,
			uv,
		}: mkShellNoCC {
			inputsFrom = [ self.finalPackage ];
			packages = [
				pylint
				uv
			];
		};
	};

	meta = {
		maintainers = with lib.maintainers; [ qyriad ];
		isBuildPythonPackage = python.meta.platforms;
	};
})
