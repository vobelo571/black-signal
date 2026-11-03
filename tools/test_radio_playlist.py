"""Run the real player initialization with small engine stubs (no game access)."""
from pathlib import Path

def run():
    from lupa.luajit21 import LuaRuntime
    path=Path(__file__).resolve().parents[1]/'modules/personal-radio/gamedata/scripts/ui_pda_radio_tab.script'
    source=path.read_bytes(); start=source.index(b'local plyr_num_of_tracks')
    block=source[start:source.index(b'local plyr_state',start)]
    fixtures=[('empty',[],1,0),('marker',['.keep'],1,0),
              ('mixed',['.keep','flx_0001.ogg','notes.txt','flx_0002.OGG'],2,2)]
    passed=[]
    for name,entries,want_count,want_tracks in fixtures:
        lua=LuaRuntime(encoding=None,unpack_returned_tuples=True)
        lua.globals().entries=lua.table_from([x.encode() for x in entries])
        lua.execute(b'''
            num_of_plyr=1; common_playlist_folders={5}; path_plyr={[5]='radio\\\\_playlist_5\\\\'}
            FS={FS_ListFiles=1,FS_RootOnly=2}; bit_or=function(a,b) return a+b end
            calls={}; sound_object=function(path) calls[#calls+1]=path; return path end
            function getFS() return {file_list_open=function()
                return {Size=function() return #entries end, GetAt=function(self,i) return entries[i+1] end}
            end} end
        ''')
        count,tracks,display=lua.execute(block+b'\nreturn plyr_num_of_tracks[1], plyr_tracks[1], plyr_tracks_display[1]')
        assert count==want_count,(name,count)
        assert display[1] is not None,name
        assert len(lua.globals().calls)==max(want_tracks,1),name
        if not want_tracks: assert tracks[1]==b'radio\\no_sound',tracks[1]
        passed.append(name)
    return passed

if __name__=='__main__': print('PASS:', ', '.join(run()))
