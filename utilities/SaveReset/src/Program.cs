using System.Text;
using System.Security.Cryptography;
using System.Text.Json;

record Edit(string Field, int Offset, double Before, double After);
static class Patcher {
    static byte[] Key(string name) => new byte[]{4}.Concat(BitConverter.GetBytes(name.Length)).Concat(Encoding.ASCII.GetBytes(name)).ToArray();
    static int Unique(byte[] data, byte[] needle, int start, int end) {
        int found = -1;
        for(int i=start; i<=end-needle.Length; i++) {
            if(!data.AsSpan(i,needle.Length).SequenceEqual(needle)) continue;
            if(found>=0) throw new InvalidDataException("Неоднозначная структура поля.");
            found=i;
        }
        if(found<0) throw new InvalidDataException("Нужное поле не найдено (формат не поддерживается).");
        return found+needle.Length;
    }
    public static (byte[] Data, List<Edit> Edits) Patch(byte[] original) {
        var data=(byte[])original.Clone();
        int p=Unique(data,Key("ironman").Concat(new byte[]{5,2}).ToArray(),0,data.Length);
        if(p+4>data.Length) throw new InvalidDataException("Обрезанная таблица ironman.");
        uint size=BitConverter.ToUInt32(data,p); int start=p+4;
        if(size>data.Length-start) throw new InvalidDataException("Повреждённая длина таблицы ironman.");
        int end=start+(int)size;
        var edits=new List<Edit>();
        void Set(string field,double value,int from,int to) {
            int offset=Unique(data,Key(field).Concat(new byte[]{3}).ToArray(),from,to);
            if(offset+8>to) throw new InvalidDataException("Обрезанное числовое поле.");
            double old=BitConverter.ToDouble(data,offset);
            if(!double.IsFinite(old) || Math.Abs(old)>1e9 || old!=Math.Truncate(old)) throw new InvalidDataException("Некорректный счётчик: "+field);
            BitConverter.GetBytes(value).CopyTo(data,offset);
            edits.Add(new(field,offset,old,value));
        }
        Set("death_count",0,start,end); Set("death_limit",2,start,end); Set("granted_lives",0,start,end);
        Set("deaths",0,0,data.Length);
        return(data,edits);
    }
    public static string Process(string path,string backup) {
        byte[] original=File.ReadAllBytes(path);
        var result=Patch(original);
        if(original.AsSpan().SequenceEqual(result.Data)) return "Уже готово: "+Path.GetFileName(path);
        Directory.CreateDirectory(backup);
        string stem=Path.GetFileNameWithoutExtension(path);
        foreach(string ext in new[]{".scoc",".scop",".dds"}) {
            string source=Path.ChangeExtension(path,ext);
            if(File.Exists(source)) File.Copy(source,Path.Combine(backup,stem+ext),false);
        }
        File.WriteAllText(Path.Combine(backup,stem+".report.json"),JsonSerializer.Serialize(new {File=path, SHA256=Convert.ToHexString(SHA256.HashData(original)),Changes=result.Edits},new JsonSerializerOptions{WriteIndented=true}));
        string temp=path+"."+Guid.NewGuid().ToString("N")+".tmp";
        try {
            using(var file=new FileStream(temp,FileMode.CreateNew,FileAccess.Write,FileShare.None)) {file.Write(result.Data);file.Flush(true);}
            if(!File.ReadAllBytes(temp).AsSpan().SequenceEqual(result.Data)) throw new IOException("Ошибка проверки записи.");
            if(!File.ReadAllBytes(path).AsSpan().SequenceEqual(original)) throw new IOException("Сейв изменился во время обработки. Закройте игру.");
            File.Replace(temp,path,null);
        } finally {if(File.Exists(temp)) File.Delete(temp);}
        return "Готово: "+Path.GetFileName(path);
    }
    public static void Test(string folder,string report) {
        var lines=new List<string>(); int count=0;
        foreach(var file in Directory.GetFiles(folder,"*.scoc")) {
            var original=File.ReadAllBytes(file); var r=Patch(original);
            if(r.Data.Length!=original.Length) throw new Exception("Length changed");
            for(int i=0;i<original.Length;i++) if(original[i]!=r.Data[i] && !r.Edits.Any(e=>i>=e.Offset && i<e.Offset+8)) throw new Exception("Unexpected change");
            if(!Patch(r.Data).Data.AsSpan().SequenceEqual(r.Data)) throw new Exception("Not idempotent");
            string sandbox=Path.Combine(Path.GetTempPath(),"SaveResetTest-"+Guid.NewGuid());Directory.CreateDirectory(sandbox);
            string target=Path.Combine(sandbox,Path.GetFileName(file));File.WriteAllBytes(target,original);
            string backup=Path.Combine(sandbox,"backup");Process(target,backup);
            if(!File.ReadAllBytes(target).AsSpan().SequenceEqual(r.Data)) throw new Exception("Write failed");
            if(!original.AsSpan().SequenceEqual(r.Data) && !File.ReadAllBytes(Path.Combine(backup,Path.GetFileName(file))).AsSpan().SequenceEqual(original)) throw new Exception("Backup failed");
            lines.Add(Path.GetFileName(file)+": OK "+JsonSerializer.Serialize(r.Edits)); count++;
        }
        try{Patch(new byte[100]);throw new Exception("Invalid accepted");}catch(InvalidDataException){}
        lines.Insert(0,$"PASS: {count} saves, exact byte changes, idempotence, backup and atomic write; invalid format rejected. Originals untouched.");
        File.WriteAllLines(report,lines);
    }
}
class MainWindow:Form {
    TextBox folder=new(){Text=@"D:\Anomaly\appdata\savedgames",Dock=DockStyle.Fill};
    TextBox log=new(){Multiline=true,ReadOnly=true,ScrollBars=ScrollBars.Both,Dock=DockStyle.Fill,WordWrap=false};
    Button run=new(){Text="Обнулить смерти и установить 2 жизни",AutoSize=true,Height=40};
    Button browse=new(){Text="Выбрать папку…",AutoSize=true};
    public MainWindow() {
        Text="GAMMA — Смерти: 0 · Жизни: 2";Width=850;Height=550;MinimumSize=new(650,400);StartPosition=FormStartPosition.CenterScreen;
        Font=new("Segoe UI",10);
        var layout=new TableLayoutPanel{Dock=DockStyle.Fill,Padding=new(16),ColumnCount=2,RowCount=5};
        layout.ColumnStyles.Add(new(SizeType.Percent,100));layout.ColumnStyles.Add(new(SizeType.AutoSize));
        layout.RowStyles.Add(new(SizeType.AutoSize));layout.RowStyles.Add(new(SizeType.AutoSize));layout.RowStyles.Add(new(SizeType.AutoSize));layout.RowStyles.Add(new(SizeType.AutoSize));layout.RowStyles.Add(new(SizeType.Percent,100));
        var info=new Label{Text="Пакетная обработка всех сейвов в выбранной папке.\nПеред запуском закройте игру. Резервные копии сохраняются в подпапке SaveReset_Backups.",AutoSize=true,Margin=new(0,0,0,16)};
        layout.Controls.Add(info,0,0);layout.SetColumnSpan(info,2);
        layout.Controls.Add(folder,0,1);layout.Controls.Add(browse,1,1);
        layout.Controls.Add(run,0,2);layout.SetColumnSpan(run,2);
        var note=new Label{Text="Меняются только счётчики в .scoc. Вложенные папки не обрабатываются.",AutoSize=true,Margin=new(0,10,0,10)};
        layout.Controls.Add(note,0,3);layout.SetColumnSpan(note,2);layout.Controls.Add(log,0,4);layout.SetColumnSpan(log,2);Controls.Add(layout);
        browse.Click+=(_,_)=>{using var dialog=new FolderBrowserDialog{InitialDirectory=folder.Text};if(dialog.ShowDialog()==DialogResult.OK)folder.Text=dialog.SelectedPath;};
        run.Click+=async(_,_)=>{
            string root=folder.Text.Trim();if(!Directory.Exists(root)){MessageBox.Show("Папка не найдена.");return;}
            run.Enabled=browse.Enabled=folder.Enabled=false;log.Clear();
            try {
                string[] files=Directory.GetFiles(root,"*.scoc");
                string backup=Path.Combine(root,"SaveReset_Backups",DateTime.Now.ToString("yyyy-MM-dd_HH-mm-ss")+"_"+Guid.NewGuid().ToString("N")[..6]);
                int done=0,errors=0;
                foreach(var file in files) {
                    try{string message=await Task.Run(()=>Patcher.Process(file,backup));log.AppendText(message+Environment.NewLine);done++;}
                    catch(Exception ex){log.AppendText("Пропущен: "+Path.GetFileName(file)+" — "+ex.Message+Environment.NewLine);errors++;}
                }
                log.AppendText($"\r\nОбработано: {done}. Пропущено: {errors}.\r\n");
                if(Directory.Exists(backup))log.AppendText("Резервные копии: "+backup+"\r\n");
                if(files.Length==0)log.AppendText("Файлы .scoc не найдены. Выберите папку savedgames.\r\n");
            } catch(Exception ex){log.AppendText(ex.Message);}finally{run.Enabled=browse.Enabled=folder.Enabled=true;}
        };
    }
}
static class Program {
    [STAThread] static void Main(string[] args) {
        if(args.Length==3 && args[0]=="--self-test") {Patcher.Test(args[1],args[2]);return;}
        ApplicationConfiguration.Initialize();Application.Run(new MainWindow());
    }
}
