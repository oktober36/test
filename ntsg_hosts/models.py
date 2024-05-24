from re import fullmatch
from typing import Literal

from python_hosts import Hosts as _Hosts, HostsEntry as _HostsEntry

NTSG_BLOCK_BEGIN = "# NTSG BEGIN записи узлов NTSG кластера"

NTSG_BLOCK_END = "#  NTSG END"


class _NTSGEntryCore(_HostsEntry):
    ...


class NTSGEntry(_NTSGEntryCore):
    def __init__(self, address: str, name: str, entry_type: Literal["ipv4", "ipv6"] = "ipv4"):
        super().__init__(address=address, names=[name], entry_type=entry_type)

    @property
    def name(self):
        return self.names[0]

    @name.setter
    def name(self, value):
        self.names[0] = value


class NTSGHosts(_Hosts):
    __slots__ = tuple()

    def __init__(self, path=None, **kwargs):
        super().__init__(path=path, **kwargs)

    def populate_entries(self):
        try:
            with open(self.path, 'r') as hosts_file:
                hosts_entries = [line for line in hosts_file]

                entry_class = _HostsEntry
                for hosts_entry in hosts_entries:
                    entry_type = _HostsEntry.get_entry_type(hosts_entry)
                    if entry_type == "comment":
                        hosts_entry = hosts_entry.replace("\r", "")
                        hosts_entry = hosts_entry.replace("\n", "")

                        if hosts_entry == NTSG_BLOCK_BEGIN:
                            entry_class = _NTSGEntryCore

                        elif hosts_entry == NTSG_BLOCK_END:
                            entry_class = _HostsEntry
                        else:
                            self.entries.append(entry_class(entry_type="comment",
                                                            comment=hosts_entry))

                    elif entry_type in ("ipv4", "ipv6"):
                        split_entry = hosts_entry.split('#', 1)
                        chunked_entry = split_entry[0].split()
                        comment = None
                        if len(split_entry) == 2:
                            comment = split_entry[1].strip()
                        stripped_name_list = [name.strip() for name in
                                              chunked_entry[1:]]

                        self.entries.append(
                            entry_class(
                                entry_type=entry_type,
                                address=chunked_entry[0].strip(),
                                names=stripped_name_list,
                                comment=comment))
        except IOError:
            return {'result': 'failed',
                    'message': 'Cannot read: {0}.'.format(self.path)}

    def write(self, path=None, mode='w'):
        if path is None:
            path = self.path

        ntsg_entries = [entry for entry in self.entries if issubclass(type(entry), _NTSGEntryCore)]
        outer_entries = [entry for entry in self.entries if not issubclass(type(entry), _NTSGEntryCore)]

        self.entries = outer_entries
        super().write(path, mode)

        if ntsg_entries:
            with open(path, "a") as file:
                file.write(f"\n{NTSG_BLOCK_BEGIN}\n")
            self.entries = ntsg_entries
            super().write(path, "a")
            with open(path, "a") as file:
                file.write(f"\n{NTSG_BLOCK_END}\n")

    def add(self, entry: NTSGEntry | tuple[str, str, str] | tuple[str, str]):
        if isinstance(entry, tuple):
            entry = NTSGEntry(*entry)

        cur_name = entry.name

        existed_names = filter(lambda entry_: cur_name in entry_.names, self.entries)
        for entr in existed_names:
            if len(entr.names) == 1:
                del entr
            else:
                entr.names.remove(cur_name)

        super().add([entry], force=True)

    def remove(self, name: str, include_outer_entries=False):
        if include_outer_entries:
            self.entries = [entry for entry in self.entries if name not in entry.names]
        else:
            self.entries = [entry
                            for entry in self.entries
                            if not issubclass(type(entry), _NTSGEntryCore)
                            or name not in entry.names]

    def clear(self, include_outer_entries=False):
        if include_outer_entries:
            self.entries = []
        else:
            self.entries = [entry for entry in self.entries if not issubclass(type(entry), _NTSGEntryCore)]

    def get_name_by_address(self, address: str, include_outer_entries=False):
        if include_outer_entries:
            return sum(entry.names for entry in self.entries if entry.address == address)
        else:
            return sum(entry.names
                       for entry in self.entries
                       if issubclass(type(entry), _NTSGEntryCore)
                       and entry.address == address)

    def get_address_by_name(self, name: str, include_outer_entries=False):
        if include_outer_entries:
            return [entry.address for entry in self.entries if name in entry.names]
        else:
            return [entry.address
                    for entry in self.entries
                    if issubclass(type(entry), _NTSGEntryCore)
                    and name in entry.names]

    def get_address_by_regexp(self, regexp: str, include_outer_entries=False):
        """
        Поиск адресов по регуляркам имен
        :param regexp:
        :param include_outer_entries:
        :return:
        """
        if include_outer_entries:
            return [entry.address for entry in self.entries if any(fullmatch(regexp, name) for name in entry.names)]
        else:
            return [entry.address
                    for entry in self.entries
                    if issubclass(type(entry), _NTSGEntryCore)
                    and any(fullmatch(regexp, name) for name in entry.names)]

    def contains(self, *, name: str=None, address:str = None, include_outer_entries=False):
        if include_outer_entries:
            found_entries = self.entries
        else:
            found_entries = [entry for entry in self.entries if issubclass(type(entry), _NTSGEntryCore)]

        if name is not None:
            found_entries = [entry for entry in found_entries if name in entry.names]
        if address is not None:
            found_entries = [entry for entry in found_entries if entry.address == address]

        return bool(found_entries)

    def __contains__(self, name: str):
        return self.contains(name=name)



