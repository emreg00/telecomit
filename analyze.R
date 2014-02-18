
data.dir<-"../data/output/" 

library(ggplot2)
library(reshape)

main<-function() {
    draw()
}

draw<-function() {
    file.name = paste(data.dir, "combined.dat", sep="")
    d = read.table(file.name, header=T)
    #ggplot(data=d, aes(x=timestap)) + geom_line(aes(y=speed)) + geom_point(aes(y=intensity))
    # e=melt(d, "condition")
    #e=d[d$intensity>0,]

    # Plot values for one grid
    #p = ggplot(data = d, aes_string(x = variable, y = selected)) + geom_point(aes(size = factor(m), color=factor(flag), alpha=1)) + geom_hline(aes_string(yintercept=cutoff)) + theme_bw() + labs(y="P-value") + guides(size=guide_legend("N target"), color=guide_legend("Indication"), alpha=F) 
    #print(p)

    pdf(sub("\\.dat", ".pdf", file.name), onefile=T)
    for(id in c(1281, 4357, 4358, 4359)) {
	e = d
	e = e[e$grid==id,]
	a = max(e$intensity)
	e$intensity = 100*e$intensity/a
	a = max(e$speed)
	e$speed = 100*e$speed/a
	#e$intensity = scale(e$intenstiy) #e$intensity/max(e$intensity)
	#e$speed = scale(e$speed) #e$speed/max(e$speed)
	plot(e$t, e$intensity, col=2, type="l", main=paste("grid id:", id), ylab="Ratio compared to max (%)")
	lines(e$t, e$speed, col=3)
    }
    dev.off()
}

main()

