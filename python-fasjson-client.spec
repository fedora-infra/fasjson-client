%global pypi_name fasjson-client
%global pypi_underscore_name %{lua:s = string.gsub(rpm.expand("%pypi_name"), "-", "_"); print(s)}

# EL8 doesn't know the __default_python3_pkgversion macro
%if ! 0%{?__default_python3_pkgversion:1}
%global __default_python3_pkgversion %(%__python3 -c 'import sys; print(".".join(str(d) for d in sys.version_info[:2]))' || echo 3)
%endif

%define py3verdist() python%{__default_python3_pkgversion}dist(%1)

%if ! 0%{?rhel} || 0%{?rhel} >= 9
%bcond_without tests
%else
%bcond_with tests
%endif

Name:           python-%{pypi_name}
Version:        1.0.7
Release:        %autorelease
Summary:        An OpenAPI client for FASJSON

License:        LGPLv3+
URL:            https://github.com/fedora-infra/fasjson-client
Source0:        %{pypi_source}
BuildArch:      noarch

# Split off fasjson-client into subpackage
Obsoletes:      python3-fasjson-client < 0.1.1

BuildRequires:  python3-devel
BuildRequires:  %{py3verdist setuptools}
# runtime
BuildRequires:  (%{py3verdist bravado} >= 10.6 with %{py3verdist bravado} < 12)
BuildRequires:  (%{py3verdist click} >= 6.7 with %{py3verdist click} < 9)
BuildRequires:  (%{py3verdist cryptography} >= 2.3 with %{py3verdist cryptography} < 37)
BuildRequires:  (%{py3verdist gssapi} >= 1.5.1 with %{py3verdist gssapi} < 2)
BuildRequires:  (%{py3verdist requests} >= 2.20.0 with %{py3verdist requests} < 3)
BuildRequires:  (%{py3verdist requests-gssapi} >= 1.2.1 with %{py3verdist requests-gssapi} < 2)
%if %{with tests}
BuildRequires:  (%{py3verdist toml} >= 0.10.1 with %{py3verdist toml} < 0.11)
%else
# EL <= 8
BuildRequires:  (%{py3verdist toml} >= 0.10.0 with %{py3verdist toml} < 0.11)
%endif
# unit tests
%if %{with tests}
BuildRequires:  (%{py3verdist coverage} >= 5.0.3 with %{py3verdist coverage} < 6)
BuildRequires:  (%{py3verdist pytest} >= 4.6.11 with %{py3verdist pytest} < 7)
BuildRequires:  (%{py3verdist pytest-cov} >= 2.8.1 with %{py3verdist pytest-cov} < 4)
BuildRequires:  (%{py3verdist pytest-mock} >= 1.10.4 with %{py3verdist pytest-mock} < 4)
BuildRequires:  (%{py3verdist requests-mock} >= 1.7 with %{py3verdist requests-mock} < 2)
%endif

%description
A python client library for the FASJSON API.

%package -n     python3-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pypi_name}}

%if 0%{?rhel} && 0%{?rhel} < 9
# Undefined deps of deps in EL8
# (-> bravado-core, -> swagger-spec-validator) -> jsonschema
Requires:       %{py3verdist attrs}
Requires:       %{py3verdist idna}
Requires:       %{py3verdist jsonpointer}
Requires:       %{py3verdist rfc3987}
Requires:       %{py3verdist setuptools}
Requires:       %{py3verdist six}
Requires:       %{py3verdist strict-rfc3339}
Requires:       %{py3verdist webcolors}
%endif

%description -n python3-%{pypi_name}
A python client library for the FASJSON API.

%{?python_extras_subpkg:%python_extras_subpkg -n python3-%{pypi_name} -i %{python3_sitelib}/%{pypi_underscore_name}*.egg-info cli}

%package -n     fasjson-client
Summary:        %{summary} - CLI
Requires:       python3-%{pypi_name}%{?python_extras_subpkg:+cli} = %{version}-%{release}
Obsoletes:      python3-fasjson-client < 0.1.1

%if 0%{?rhel} && 0%{?rhel} < 9
Requires:       %{py3verdist click}
Requires:       %{py3verdist cryptography}
%endif

%description -n fasjson-client
A command line interface for the FASJSON API.

%prep
%autosetup -n %{pypi_name}-%{version}

%build
%py3_build

%install
%py3_install

%if %{with tests}
%check
%{__python3} -m pytest -v
%endif

%files -n python3-%{pypi_name}
%license LICENSE
%doc README.md
%{python3_sitelib}/fasjson_client
%{python3_sitelib}/fasjson_client-%{version}-py%{python3_version}.egg-info

%files -n fasjson-client
%license LICENSE
%{_bindir}/fasjson-client


%changelog
%autochangelog
