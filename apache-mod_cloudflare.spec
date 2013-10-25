%define		mod_name	cloudflare
%define 	apxs		%{_sbindir}/apxs
Summary:	Apache module to show true visitor IPs in logs for domains using CloudFlare
Name:		apache-mod_%{mod_name}
Version:	1.2.0
Release:	1
License:	Apache v2.0
Group:		Networking/Daemons/HTTP
Source0:	https://github.com/cloudflare/mod_cloudflare/archive/master/mod_%{mod_name}-%{version}.tar.gz
# Source0-md5:	d87e1c38dba2c282bfae9341e0f3c3e7
Source1:	apache.conf
BuildRequires:	apache-devel >= 2.2
BuildRequires:	rpmbuild(macros) >= 1.268
Requires:	apache(modules-api) = %apache_modules_api
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)/conf.d

%description
CloudFlare acts as a proxy, which means that your visitors are routed
through the CloudFlare network and you do not see their original IP
address.

This module uses HTTP headers provided by the CloudFlare proxy to log
the real IP address of the visitor. Based on mod_remoteip.c, this
apache extension will replace the remote_ip variable in user's logs
with the correct remote_ip sent from CloudFlare. This also does
authentication, only performing the switch for requests originating
from CloudFlare IPs.

%prep
%setup -qc
mv mod_cloudflare-*/* .

%build
%{apxs} -c mod_%{mod_name}.c -o mod_%{mod_name}.so

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}}
install -p mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/90_mod_%{mod_name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
%service -q httpd restart

%postun
if [ "$1" = "0" ]; then
	%service -q httpd restart
fi

%files
%defattr(644,root,root,755)
%doc README.md
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*_mod_%{mod_name}.conf
%attr(755,root,root) %{_pkglibdir}/mod_%{mod_name}.so
